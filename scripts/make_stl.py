import numpy as np, trimesh as tm
S=8.0
def sph(r,c,sc=(1,1,1),sub=3):
    m=tm.creation.icosphere(subdivisions=sub,radius=r); m.apply_scale(sc); m.apply_translation(c); return m
def rod(a,b,r): return tm.creation.cylinder(radius=r,segment=np.array([a,b]),sections=12)
def unit(v): return v/np.linalg.norm(v)
# --- shell with windows (stands in for the transparent membrane) ---
phi=(1+5**.5)/2
V=np.array([[-1,phi,0],[1,phi,0],[-1,-phi,0],[1,-phi,0],[0,-1,phi],[0,1,phi],[0,-1,-phi],[0,1,-phi],[phi,0,-1],[phi,0,1],[-phi,0,-1],[-phi,0,1]],float)
V=np.array([unit(v) for v in V]); ico=tm.Trimesh(V*1.0,tm.convex.convex_hull(V).faces,process=False)
FC=np.array([unit(V[f].sum(0)) for f in tm.convex.convex_hull(V).faces])
RO,RI,HOLE=5.0,4.75,1.05
shell=sph(RO,(0,0,0),sub=4).difference(sph(RI,(0,0,0),sub=4),engine='manifold')
holes=[tm.creation.cylinder(radius=HOLE,segment=np.array([f*3,f*6]),sections=32) for f in FC]
shell=shell.difference(tm.boolean.union(holes,engine='manifold'),engine='manifold')
def wall_dir(d):                       # keep struts on the ribs, not in a window
    d=unit(d)
    for _ in range(20):
        i=np.argmax(FC@d); f=FC[i]
        if np.linalg.norm(d*RO-f*RO)>HOLE+.5: break
        d=unit(d+.25*unit(d-f))
    return d
parts=[shell]
def tether(c,r=.17):
    d=wall_dir(c); parts.append(rod(c,d*4.9,r))
# --- layout read off the screenshot (x,y in cell units; z chosen so each sits inside the cell) ---
def zfor(x,y,R,s): return s*np.sqrt(max(R*R-x*x-y*y,.2))
# nucleus, ER, golgi: same shapes as the sim, turned by the sim's rotation (golgi lands at x=.27)
G0=np.array([-2.8,-1.5,1.6]); best=min(np.linspace(0,6.283,3600),key=lambda t:abs(G0[0]*np.cos(t)+G0[2]*np.sin(t)-.27)+ (G0[2]*np.cos(t)-G0[0]*np.sin(t)<0)*10)
Ry=lambda p: np.array([p[0]*np.cos(best)+p[2]*np.sin(best),p[1],-p[0]*np.sin(best)+p[2]*np.cos(best)])
NC=Ry([.3,.2,0.]); parts.append(sph(1.6,NC,sub=4)); parts.append(sph(.55,NC+unit(Ry([.6,.4,.3])-NC+[.0,.0,.0]*1)*1.3 if False else Ry([.6,.4,.3])+[0,0,.0],sub=3))
pts=[]
N=180
for i in range(N+1):
    u=i/N*4*np.pi; q=1.5*u; c=np.cos(q)
    pts.append(Ry(np.array([(2+c)*.5*np.cos(u),(2+c)*.5*np.sin(u),np.sin(q)*.5])*2+[.3,.2,0]))
er=tm.boolean.union([sph(.28,p,sub=2) for p in pts]+[rod(pts[i],pts[i+1],.28) for i in range(N)],engine='manifold'); parts.append(er)
for i in range(0,N,8): parts.append(sph(.2,pts[i]+unit(pts[i]-NC)*.3,sub=2))
for k in (0,1,2):                       # ER anchored to the cage
    p=max(pts[k*60:(k+1)*60],key=lambda p:np.linalg.norm(p)); tether(p,.2)
Gc=Ry(G0)
for i in range(5):
    t=tm.creation.torus(major_radius=1.1-i*.05,minor_radius=.12,major_sections=36,minor_sections=10); t.apply_translation(Gc+[0,i*.28,0]); parts.append(t)
parts.append(rod(Gc+[0,.5,0],NC+[0,-.8,.6],.25)); tether(Gc+[0,.5,0],.22)
# mitochondria (center x,y ; long-axis direction as seen in the image)
M=[((-3.43,.93),(1,.65),1),((-2.03,1.03),(.25,1),1),((-1.09,1.52),(1,-.9),-1),((3.48,2.14),(1,-.45),1),((2.53,.86),(1,-.65),-1),((3.69,.78),(.5,1),1),((2.70,-.86),(.35,-1),1)]
for (x,y),ax,s in M:
    R=min(max(3.4,np.hypot(x,y)+.6),4.2); c=np.array([x,y,zfor(x,y,R,s)])
    a=unit(np.array([ax[0],ax[1],0.])); b=unit(np.cross(a,[0,0,1])); z=np.cross(a,b)
    m=sph(.45,(0,0,0),(2.1,.9,.9)); Rm=np.eye(4); Rm[:3,0]=a; Rm[:3,1]=b; Rm[:3,2]=z; m.apply_transform(Rm); m.apply_translation(c)
    parts.append(m); tether(c)
for (x,y),s in [((-3.93,1.55),1),((-1.47,-.15),1),((-2.87,-.56),-1),((-2.87,-.99),1),((-3.5,.37),-1)]:
    c=np.array([x,y,zfor(x,y,3.6,s)]); parts.append(sph(.33,c)); tether(c)
body=tm.boolean.union(parts,engine='manifold'); body.apply_scale(S)
body.apply_translation(-body.centroid*[1,0,1]+[0,-body.bounds[0][1],0])
parts_cc=body.split(only_watertight=False)
print('watertight',body.is_watertight,'pieces',len(parts_cc),'extents mm',body.extents.round(1),'faces',len(body.faces))
body.export('../models/dino_cell_full.stl')
