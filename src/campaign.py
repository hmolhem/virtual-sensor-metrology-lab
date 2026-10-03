from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
import pandas as pd

from .config_boundary import load_private_truth, load_public_config
from .experiments import build_all_test_matrices
from .utils import quantize_positive

FILES={"static":"static_measurements.csv","step":"dynamic_step_measurements.csv","ramp":"ramp_measurements.csv","cyclic":"cyclic_measurements.csv","sinusoidal":"sinusoidal_measurements.csv","stability":"stability_measurements.csv"}
FORBIDDEN=("true_","_truth","latent","noise","raw_prequant","dynamic_state","day_effect","run_effect","private","injected")

def root(): return Path(__file__).resolve().parents[1]
def loadj(path):
    with Path(path).open("r",encoding="utf-8") as f: x=json.load(f)
    if not isinstance(x,dict): raise ValueError(f"JSON root must be object: {path}")
    return x
def private_hash(x):
    s=json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return hashlib.sha256(s.encode()).hexdigest()
def check_commitment(truth,commitment):
    if truth.get("personality_id")!=commitment.get("personality_id") or private_hash(truth)!=commitment.get("sha256"):
        raise ValueError("Frozen hidden personality commitment mismatch.")
def safe(df,name):
    bad=[c for c in df.columns if any(t in str(c).lower() for t in FORBIDDEN)]
    if bad: raise ValueError(f"{name} leaks simulator-only columns: {bad}")

def rngs(master,fam):
    ss=np.random.SeedSequence(master).spawn(6)[fam].spawn(4)
    return {k:np.random.default_rng(s) for k,s in zip(("ch","ref","dut","aux"),ss)}
def delay(t,x,d): return np.interp(t-d,t,x,left=float(x[0]),right=float(x[-1]))
def fo(x,dt,tau,y0=None):
    x=np.asarray(x,float); y=np.empty_like(x); y[0]=x[0] if y0 is None else y0; a=math.exp(-dt/tau)
    for k in range(1,len(x)): y[k]=a*y[k-1]+(1-a)*x[k-1]
    return y
def motion(cmd,initial=1):
    d=np.diff(cmd,prepend=cmd[0]); out=np.empty(len(cmd)); cur=1. if initial>=0 else -1.
    for i,v in enumerate(d):
        if v>1e-12: cur=1.
        elif v<-1e-12: cur=-1.
        out[i]=cur
    return out
def dut_fo(x,t,temp,mot,p):
    dyn=p["dut_truth"]["dynamics"]; y=np.empty_like(x); y[0]=x[0]
    for k in range(1,len(x)):
        base=dyn["tau_up_s"] if mot[k-1]>=0 else dyn["tau_down_s"]
        tau=max(.1,base*(1+dyn["tau_temperature_coefficient_per_c"]*(temp[k-1]-25)))
        a=math.exp(-(t[k]-t[k-1])/tau); y[k]=a*y[k-1]+(1-a)*x[k-1]
    return y
def ref_measure(x,day,p,r):
    s=p["reference_truth"]["static"]; d=p["reference_truth"]["drift"]
    n=r.normal(0,s["repeatability_sigma_rh_percent"],len(x)); raw=np.asarray(x)+s["bias_rh_percent"]+d["annual_rh_percent"]*day/365+n
    return raw,quantize_positive(raw,s["resolution_rh_percent"]),n
def dut_measure(x,temp,day,hs,p,de,re,r):
    s=p["dut_truth"]["static"]; d=p["dut_truth"]["drift"]; xc=np.asarray(x)-50; tc=np.asarray(temp)-25
    err=(s["offset_rh_percent"]+(s["gain_scale"]-1)*xc+s["quadratic_coefficient_rh_per_rh2"]*xc**2+s["temperature_coefficient_rh_percent_per_c"]*tc+s["rh_temperature_interaction_rh_per_rh_c"]*xc*tc+.5*s["hysteresis_loop_width_rh_percent"]*np.asarray(hs)+d["annual_rh_percent"]*day/365+de+re)
    n=r.normal(0,s["repeatability_sigma_rh_percent"],len(x)); raw=np.asarray(x)+err+n
    return raw,quantize_positive(raw,s["resolution_rh_percent"]),n,err
def chamber_static(rh,temp,n,p,r):
    s=p["chamber_truth"]["static"]; rf=r.normal(0,s["stability_sigma_rh_percent"],n); tf=r.normal(0,s["temperature_stability_sigma_c"],n)
    base=rh+s["setpoint_bias_rh_percent"]+rf; T=temp+s["temperature_bias_c"]+tf
    return base+s["spatial_offset_dut_rh_percent"],base+s["spatial_offset_reference_rh_percent"],T,rf,tf
def chamber_dyn(cmd,temp,t,p,r,step=None):
    s=p["chamber_truth"]["static"]; d=p["chamber_truth"]["dynamics"]; m=motion(cmd,np.sign(cmd[-1]-cmd[0]) or 1)
    u=delay(t,cmd,d["dead_time_s"]); y=np.empty_like(u); y[0]=u[0]+s["setpoint_bias_rh_percent"]
    for k in range(1,len(u)):
        tau=d["tau_up_s"] if m[k-1]>=0 else d["tau_down_s"]; a=math.exp(-(t[k]-t[k-1])/tau)
        y[k]=a*y[k-1]+(1-a)*(u[k-1]+s["setpoint_bias_rh_percent"])
    if step:
        ts,a0,a1=step; z=np.maximum(t-ts,0); tau=(d["tau_up_s"] if a1>a0 else d["tau_down_s"])/3
        pulse=(z/max(5,tau))*np.exp(1-z/max(5,tau)); pulse[t<ts]=0
        y+=np.sign(a1-a0)*abs(a1-a0)*d["overshoot_fraction"]*pulse
    y+=d["cycling_amplitude_rh_percent"]*np.sin(2*np.pi*t/d["cycling_period_s"])+r.normal(0,s["stability_sigma_rh_percent"],len(t))
    T=temp+s["temperature_bias_c"]+r.normal(0,s["temperature_stability_sigma_c"],len(t))
    return y+s["spatial_offset_dut_rh_percent"],y+s["spatial_offset_reference_rh_percent"],T,y,m
def dyn_chain(cmd,temp,t,p,R,re=0,step=None):
    xd,xr,T,ch,m=chamber_dyn(cmd,temp,t,p,R["ch"],step); rd=p["reference_truth"]["dynamics"]
    rs=fo(delay(t,xr,rd["dead_time_s"]),t[1]-t[0],rd["tau_s"],xr[0]); rr,ref,rn=ref_measure(rs,0,p,R["ref"])
    dd=p["dut_truth"]["dynamics"]; ds=dut_fo(delay(t,xd,dd["dead_time_s"]),t,T,m,p)
    dr,dut,dn,err=dut_measure(ds,T,0,-m,p,0,re,R["dut"])
    return locals()

def static_campaign(p):
    R=rngs(p["rng"]["master_seed"],0); q=p["dut_truth"]["random_effects"]
    de={d:R["dut"].normal(0,q["day_sigma_rh_percent"]) for d in (1,2,3)}; re={(d,u):R["dut"].normal(0,q["run_sigma_rh_percent"]) for d in (1,2,3) for u in (1,2)}
    count={"CALIBRATION":0,"VALIDATION":0,"CHARACTERIZATION":0}; pref={"CALIBRATION":"CAL","VALIDATION":"VAL","CHARACTERIZATION":"ST"}; A=[];P=[]
    for rh in (20.,30.,40.,50.,60.,70.,80.):
      for temp in (15.,25.,35.):
       for direction in ("UP","DOWN"):
        for day in (1,2,3):
         for run in (1,2):
          role="CALIBRATION" if rh in (20,40,60,80) and day in (1,2) else "VALIDATION" if rh in (30,50,70) and day==3 else "CHARACTERIZATION"
          count[role]+=1; tid=f"{pref[role]}-{count[role]:03d}"; n=60; t=np.arange(n,dtype=float)
          xd,xr,T,rf,tf=chamber_static(rh,temp,n,p,R["ch"]); rr,ref,rn=ref_measure(xr,day-1,p,R["ref"]); mot=np.full(n,1 if direction=="UP" else -1)
          dr,dut,dn,err=dut_measure(xd,T,day-1,-mot,p,de[day],re[(day,run)],R["dut"])
          a=pd.DataFrame({"Elapsed_s":t,"Sample_ID":np.arange(1,n+1),"Test_ID":tid,"Test_Family":"STATIC","Analysis_Role":role,"Day_ID":day,"Run_ID":run,"RH_Setpoint":rh,"Temperature_Setpoint_C":temp,"Direction":direction,"Chamber_State":"STABLE","RH_Reference":ref,"RH_DUT":dut,"Temperature_Reference_C":np.round(T,3),"Temperature_DUT_C":np.round(T,3)})
          z=a.copy(); z["RH_True_DUT"]=xd; z["RH_True_Reference"]=xr; z["Temperature_True_C"]=T; z["Reference_Raw_PreQuant"]=rr; z["DUT_Raw_PreQuant"]=dr; z["True_Day_Effect"]=de[day]; z["True_Run_Effect"]=re[(day,run)]; z["True_Reference_Noise"]=rn; z["True_DUT_Noise"]=dn
          A.append(a);P.append(z)
    return pd.concat(A,ignore_index=True),pd.concat(P,ignore_index=True)

def dynamic_family(p,fam,kind,execution):
    R=rngs(p["rng"]["master_seed"],fam); sig=p["dut_truth"]["random_effects"]["run_sigma_rh_percent"]; A=[];P=[]; jobs=[]
    if kind=="step":
        i=0
        for a,b in ((30.,70.),(70.,30.)):
         for temp in (15.,25.,35.):
          for rep in range(1,6):
           i+=1; t=np.arange(0.,301.,1.); jobs.append((f"DY-STEP-{i:03d}",t,np.where(t<60,a,b),temp,rep,"UP" if b>a else "DOWN",(60.,a,b),{}))
    elif kind=="ramp":
        i=0
        for a,b in ((30.,70.),(70.,30.)):
         for temp in (15.,25.,35.):
          for rep in range(1,4):
           i+=1; t=np.arange(0.,1201.,1.); jobs.append((f"DY-RAMP-{i:03d}",t,a+(b-a)*t/1200,temp,rep,"UP" if b>a else "DOWN",None,{}))
    elif kind=="cyclic":
        half=execution["dynamic_cyclic"]["half_cycle_s"]
        for s in range(1,4):
         t=np.arange(0.,3001.,1.); ph=np.mod(t,2*half); cmd=np.where(ph<=half,30+40*ph/half,70-40*(ph-half)/half); jobs.append((f"DY-CYC-{s:03d}",t,cmd,25.,s,None,None,{"Session":s,"Cycle_Index":np.minimum((t//(2*half)).astype(int)+1,5)}))
    else:
        cycles=execution["dynamic_sinusoidal"]["cycles_per_period"]
        for i,period in enumerate((600,300,120,60),1):
         t=np.arange(0.,cycles*period+1.,1.); cmd=50+10*np.sin(2*np.pi*t/period); jobs.append((f"DY-SIN-{i:03d}",t,cmd,25.,i,None,None,{"Period_s":period,"Frequency_Hz":1/period}))
    for tid,t,cmd,temp,rep,dir0,step,extra in jobs:
        re=R["dut"].normal(0,sig); s=dyn_chain(cmd,temp,t,p,R,re,step); direction=np.where(s["m"]>=0,"UP","DOWN") if dir0 is None else dir0; famname={"step":"DYNAMIC_STEP","ramp":"DYNAMIC_RAMP","cyclic":"DYNAMIC_CYCLIC","sinusoidal":"DYNAMIC_SINUSOIDAL"}[kind]
        data={"Elapsed_s":t,"Sample_ID":np.arange(1,len(t)+1),"Test_ID":tid,"Test_Family":famname,"RH_Command":cmd,"Temperature_Setpoint_C":temp,"Direction":direction,"Chamber_State":"TRANSIENT","RH_Reference":s["ref"],"RH_DUT":s["dut"],"Temperature_Reference_C":np.round(s["T"],3),"Temperature_DUT_C":np.round(s["T"],3)}
        if kind in ("step","ramp"): data["Repetition"]=rep
        data.update(extra); a=pd.DataFrame(data)
        if kind=="step": a.loc[a["Elapsed_s"]<60,"Chamber_State"]="STABLE"
        z=a.copy(); z["RH_True_DUT"]=s["xd"]; z["RH_True_Reference"]=s["xr"]; z["Reference_Dynamic_State"]=s["rs"]; z["DUT_Dynamic_State"]=s["ds"]; z["Reference_Raw_PreQuant"]=s["rr"]; z["DUT_Raw_PreQuant"]=s["dr"]; z["True_Run_Effect"]=re; z["True_Reference_Noise"]=s["rn"]; z["True_DUT_Noise"]=s["dn"]
        A.append(a);P.append(z)
    return pd.concat(A,ignore_index=True),pd.concat(P,ignore_index=True)

def stability_campaign(p):
    R=rngs(p["rng"]["master_seed"],5); q=p["dut_truth"]["random_effects"]; A=[];P=[]; sch=build_all_test_matrices()["stability"]
    for row in sch.to_dict("records"):
        day=int(row["Aging_Day"]); n=60; t=np.arange(n,dtype=float); de=R["dut"].normal(0,q["day_sigma_rh_percent"]); re=R["dut"].normal(0,q["run_sigma_rh_percent"])
        xd,xr,T,rf,tf=chamber_static(float(row["RH_Setpoint"]),float(row["Temperature_Setpoint_C"]),n,p,R["ch"]); rr,ref,rn=ref_measure(xr,day,p,R["ref"]); dr,dut,dn,err=dut_measure(xd,T,day,-np.ones(n),p,de,re,R["dut"])
        a=pd.DataFrame({"Elapsed_s":t,"Sample_ID":np.arange(1,n+1),"Test_ID":row["Test_ID"],"Test_Family":"STABILITY","Schedule_Type":row["Schedule_Type"],"Aging_Day":day,"RH_Setpoint":row["RH_Setpoint"],"Temperature_Setpoint_C":row["Temperature_Setpoint_C"],"Direction":"UP","Chamber_State":"STABLE","RH_Reference":ref,"RH_DUT":dut,"Temperature_Reference_C":np.round(T,3),"Temperature_DUT_C":np.round(T,3)})
        z=a.copy(); z["RH_True_DUT"]=xd; z["RH_True_Reference"]=xr; z["Reference_Raw_PreQuant"]=rr; z["DUT_Raw_PreQuant"]=dr; z["True_Day_Effect"]=de; z["True_Run_Effect"]=re; z["True_Reference_Noise"]=rn; z["True_DUT_Noise"]=dn; A.append(a);P.append(z)
    return pd.concat(A,ignore_index=True),pd.concat(P,ignore_index=True)

def all_data(p,execution):
    pairs={"static":static_campaign(p),"step":dynamic_family(p,1,"step",execution),"ramp":dynamic_family(p,2,"ramp",execution),"cyclic":dynamic_family(p,3,"cyclic",execution),"sinusoidal":dynamic_family(p,4,"sinusoidal",execution),"stability":stability_campaign(p)}
    A={k:v[0] for k,v in pairs.items()}; P={k:v[1] for k,v in pairs.items()}
    for k,v in A.items(): safe(v,k)
    return A,P

def write_release(private_path=None,output_dir=None,private_dir=None):
    R=root(); private_path=private_path or R/"config/private/final_lab_personality_v1.json"; output_dir=output_dir or R/"data/generated"; private_dir=private_dir or R/"data/private_truth"
    pub=load_public_config(); p=load_private_truth(private_path); com=loadj(R/"config/public/private_personality_commitment_v1.json"); ex=loadj(R/"config/public/campaign_execution_v1.json")
    check_commitment(p,com); A,P=all_data(p,ex); output_dir.mkdir(parents=True,exist_ok=True); private_dir.mkdir(parents=True,exist_ok=True); meta={}
    for k,df in A.items():
        path=output_dir/FILES[k]; df.to_csv(path,index=False,float_format="%.6f",lineterminator="\n"); meta[FILES[k]]={"rows":len(df),"columns":list(df.columns),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
    tm=pd.concat(list(build_all_test_matrices().values()),ignore_index=True,sort=False); path=output_dir/"test_matrix.csv"; tm.to_csv(path,index=False,float_format="%.6f",lineterminator="\n"); meta["test_matrix.csv"]={"rows":len(tm),"columns":list(tm.columns),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
    for k,df in P.items(): df.to_csv(private_dir/f"{k}_campaign_truth_v1.csv",index=False,float_format="%.6f",lineterminator="\n")
    manifest={"schema_version":"1.0","release_id":ex["release_id"],"lab":pub["lab_identity"],"hidden_personality_id":com["personality_id"],"hidden_personality_sha256_commitment":com["sha256"],"analyst_private_truth_included":False,"files":meta}
    (output_dir/"dataset_manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8"); return manifest

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--private",type=Path); ap.add_argument("--output-dir",type=Path); ap.add_argument("--private-dir",type=Path); a=ap.parse_args(); m=write_release(a.private,a.output_dir,a.private_dir); print("Generated",m["release_id"])
    for f,x in m["files"].items(): print(f,x["rows"])
    return 0
if __name__=="__main__": raise SystemExit(main())
