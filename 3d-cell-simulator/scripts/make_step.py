import numpy as np, cadquery as cq
S=8.0
V3=lambda p: cq.Vector(*[float(x)*S for x in p])
def unit(v): v=np.array(v,float); return v/np.linalg.norm(v)
def sph(r,c): return cq.Solid.makeSphere(r*S,V3(c),cq.Vector(0,1,0),-90,90,360)
def cyl(a,b,r):
    a=np.array(a,float); b=np.array(b,float); return cq.Solid.makeCylinder(r*S,np.linalg.norm(b-a)*S,V3(a),cq.Vector(*(b-a)))
phi=(1+5**.5)/2
V=np.array([unit(v) for v in [[-1,phi,0],[1,phi,0],[-1,-phi,0],[1,-phi,0],[0,-1,phi],[0,1,phi],[0,-1,-phi],[0,1,-phi],[phi,0,-1],[phi,0,1],[-phi,0,-1],[-phi,0,1]]])
import trimesh as tm
FC=np.array([unit(V[f].sum(0)) for f in tm.convex.convex_hull(V).faces])
RO,RI,HOLE=5.0,4.75,1.05
shell=sph(RO,(0,0,0)).cut(sph(RI,(0,0,0)))
for f in FC: shell=shell.cut(cyl(f*3,f*6,HOLE))
def wall_dir(d):
    d=unit(d)
    for _ in range(20):
        f=FC[np.argmax(FC@d)]
        if np.linalg.norm(d*RO-f*RO)>HOLE+.5: break
        d=unit(d+.25*unit(d-f))
    return d
parts=[shell]
def tether(c,r=.17): parts.append(cyl(c,wall_dir(c)*4.9,r))
zfor=lambda x,y,R,s: s*np.sqrt(max(R*R-x*x-y*y,.2))
G0=np.array([-2.8,-1.5,1.6]); best=min(np.linspace(0,6.283,3600),key=lambda t:abs(G0[0]*np.cos(t)+G0[2]*np.sin(t)-.27)+(G0[2]*np.cos(t)-G0[0]*np.sin(t)<0)*10)
Ry=lambda p: np.array([p[0]*np.cos(best)+p[2]*np.sin(best),p[1],-p[0]*np.sin(best)+p[2]*np.cos(best)])
NC=Ry([.3,.2,0.]); parts+= [sph(1.6,NC), sph(.55,Ry([.6,.4,.3]))]
N=120; pts=[]
for i in range(N+8):
    u=i/N*4*np.pi; q=1.5*u; c=np.cos(q)
    pts.append(Ry(np.array([(2+c)*.5*np.cos(u),(2+c)*.5*np.sin(u),np.sin(q)*.5])*2+[.3,.2,0]))
path=cq.Wire.assembleEdges([cq.Edge.makeSpline([cq.Vector(*(p*S)) for p in pts],periodic=False)])
t0=(path.tangentAt(0)); p0=path.positionAt(0)
prof=cq.Wire.makeCircle(.28*S,p0,t0)
er=cq.Solid.sweep(prof,[],path,True,True)
parts.append(er)
for i in range(0,N,6): parts.append(sph(.2,pts[i]+unit(pts[i]-NC)*.3))
for k in (0,1,2):
    p=max(pts[k*40:(k+1)*40],key=lambda p:np.linalg.norm(p)); tether(p,.2)
Gc=Ry(G0)
for i in range(5): parts.append(cq.Solid.makeTorus((1.1-i*.05)*S,.155*S,V3(Gc+[0,i*.28,0]),cq.Vector(0,1,0)))
parts.append(cyl(Gc+[0,.5,0],NC+[0,-.8,.6],.25)); tether(Gc+[0,.5,0],.22)
def ellipsoid(c,a,b,z,rx=.45*2.1,ry=.45*.9,rz=.45*.9):
    s=cq.Solid.makeSphere(1.0,cq.Vector(0,0,0),cq.Vector(0,1,0),-90,90,360)
    M=cq.Matrix([[a[0]*rx*S,b[0]*ry*S,z[0]*rz*S,c[0]*S],[a[1]*rx*S,b[1]*ry*S,z[1]*rz*S,c[1]*S],[a[2]*rx*S,b[2]*ry*S,z[2]*rz*S,c[2]*S]])
    return s.transformGeometry(M)
M=[((-3.43,.93),(1,.65),1),((-2.03,1.03),(.25,1),1),((-1.09,1.52),(1,-.9),-1),((3.48,2.14),(1,-.45),1),((2.53,.86),(1,-.65),-1),((3.69,.78),(.5,1),1),((2.70,-.86),(.35,-1),1)]
for (x,y),ax,s in M:
    R=min(max(3.4,np.hypot(x,y)+.6),4.2); c=np.array([x,y,zfor(x,y,R,s)])
    a=unit([ax[0],ax[1],0.]); b=unit(np.cross(a,[0,0,1])); z=np.cross(a,b)
    parts.append(ellipsoid(c,a,b,z)); tether(c)
for (x,y),s in [((-3.93,1.55),1),((-1.47,-.15),1),((-2.87,-.56),-1),((-2.87,-.99),1),((-3.5,.37),-1)]:
    c=np.array([x,y,zfor(x,y,3.6,s)]); parts.append(sph(.33,c)); tether(c)
print([round(p.Volume()) for p in parts[:6]],er.ShapeType())
body=parts[0]
for i,p in enumerate(parts[1:],1):
    nb=body.fuse(p).clean()
    if nb.isValid() and nb.Volume()>body.Volume()*0.98:
        body=nb
    else:
        print('skip part',i,type(p).__name__,[round(v/S,2) for v in p.Center().toTuple()],round(p.Volume()),'valid',nb.isValid(),round(nb.Volume()))
print('valid',body.isValid(),'solids',len(body.Solids()),'vol cm3',round(body.Volume()/1000,1))
bb=body.BoundingBox(); print('bbox',round(bb.xlen,1),round(bb.ylen,1),round(bb.zlen,1))
cq.exporters.export(cq.Workplane(obj=body),'../models/dino_cell_full.step')
sm=[x for x in body.Solids() if x.Volume()<1000]
for x in sm: print('small at',[round(v/S,2) for v in x.Center().toTuple()],round(x.Volume()))
print('er valid',er.isValid())
