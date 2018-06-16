#############################################################################
"""
Demo of dynamic warping for automatic picking
Author: Xinming Wu, University of Texas at Austin
Version: 2016.06.01
"""


import time
from utils import * 
setupForSubset("f3d")
s1,s2,s3 = getSamplings()
n1,n2,n3 = s1.count,s2.count,s3.count
f1,f2,f3 = s1.getFirst(),s2.getFirst(),s3.getFirst()
d1,d2,d3 = s1.getDelta(),s2.getDelta(),s3.getDelta()
#############################################################################
gxfile = "gx" # input semblance image
p2file = "p2" # inline slopes
p3file = "p3" # crossline slopes
epfile = "ep"  # planarity
c2file = "c2" # c2 coherence or semblance-based coherence
c2sfile = "c2s" # c2 coherence or semblance-based coherence
c3file = "c3" # c3 coherence or covariance-based coherence
smsfile = "sms" # structure-oriented semblance
epsfile = "eps" # structure-oriented planarity
effile = "ef"  # 1-planarity
fefile = "fe"  # 1-planarity
flfile = "fl"  # fault likelihood
fpfile = "fp"  # fault strike;
ftfile = "ft"  # fault dip;
fvfile = "fv"  # fault dip;
vpfile = "vp"  # fault dip;
vtfile = "vt"  # fault dip;
fetfile = "fet" # fault likelihood thinned
fptfile = "fpt" # fault strike thinned
fttfile = "ftt" # fault dip thinned
fskfile = "skin"

plotOnly = False
plotOnly = True
pngDir = None
pngDir = getPngDir()
# These parameters control the scan over fault strikes and dips.
# See the class FaultScanner for more information.
minTheta,maxTheta = 65,80
minPhi,maxPhi = 0,360
sigmaPhi,sigmaTheta=3,6

def main(args):
  #goSlopes()
  #goC2()
  #goC2s()
  #goC3()
  #goPlanar()
  #goStructureOrientedSemblance()
  #goStructureOrientedPlanarity()
  #goFaultLikelihoodScan()
  goFaultLikelihood()
  #goFaultOrientScan()
  #goSurfaceVoting()
  #goFaultSurfaces()
  #goFaultLikelihood()
  #goFaultSkins()
  #goVoters()

def goSlopes():
  gx = readImage3D(gxfile)
  p2 = zerofloat(n1,n2,n3)
  p3 = zerofloat(n1,n2,n3)
  lsf = LocalSlopeFinder(8,2,2,5)
  lsf.findSlopes(gx,p2,p3)
  writeImage(p2file,p2)
  writeImage(p3file,p3)

# a simplified C2 coherence method
# (Marfurt, Kirlin, Farmer and Bahorich, 1998)
def goC2():
  sig1,sig2,sig3 = 16,1,1 
  gx = readImage3D(gxfile)
  if not plotOnly:
    ref1 = RecursiveExponentialFilter(sig1)
    ref2 = RecursiveExponentialFilter(sig2)
    ref3 = RecursiveExponentialFilter(sig3)
    ref1.setEdges(RecursiveExponentialFilter.Edges.OUTPUT_ZERO_SLOPE)
    ref2.setEdges(RecursiveExponentialFilter.Edges.OUTPUT_ZERO_SLOPE)
    ref3.setEdges(RecursiveExponentialFilter.Edges.OUTPUT_ZERO_SLOPE)
    gn = zerofloat(n1,n2,n3)
    gd = zerofloat(n1,n2,n3)
    start = time.time()
    # compute the numerator of coherence
    ref2.apply2(gx,gn)
    ref3.apply3(gn,gn)
    gn = mul(gn,gn)
    ref1.apply1(gn,gn)
    # compute the denominator of coherence
    gd = mul(gx,gx)
    ref2.apply2(gd,gd)
    ref3.apply3(gd,gd)
    ref1.apply1(gd,gd)
    c2 = div(gn,gd)
    print "C2 time:"
    print (time.time()-start)
    writeImage(c2file,c2)
  else:
    c2 = readImage3D(c2file)
  c2 = pow(c2,8)
  plot3(gx,sub(1,c2),cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
        clab="1-coherence",png="c2")
def goC2s():
  sig1,sig2,sig3 = 16,1,1 
  gx = readImage3D(gxfile)
  if not plotOnly:
    lof = LocalOrientFilter(8,2)
    ets = lof.applyForTensors(gx)
    ets.setEigenvalues(0.0001,1.0,1.0)
    lsf = LocalSmoothingFilter()
    ref1 = RecursiveExponentialFilter(sig1)
    ref1.setEdges(RecursiveExponentialFilter.Edges.OUTPUT_ZERO_SLOPE)
    gn = zerofloat(n1,n2,n3)
    gd = zerofloat(n1,n2,n3)
    start = time.time()
    # compute the numerator of coherence
    lsf.apply(ets,sig2,gx,gn)
    gn = mul(gn,gn)
    ref1.apply1(gn,gn)
    # compute the denominator of coherence
    lsf.apply(ets,sig2,mul(gx,gx),gd)
    ref1.apply1(gd,gd)
    c2s = div(gn,gd)
    print "C2s time:"
    print (time.time()-start)
    writeImage(c2sfile,c2s)
  else:
    c2s = readImage3D(c2sfile)
  c2s = pow(c2s,8)
  plot3(gx,sub(1,c2s),cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
        clab="1-coherence",png="c2s")
# covariance-matrix-based semblance
# (Gersztenkorn and Marfurt, 1999)
def goC3():
  gx = readImage3D(gxfile)
  if not plotOnly:
    p2 = readImage3D(p2file)
    p3 = readImage3D(p3file)
    start=time.time()
    cv = Covariance()
    em,es = cv.covarianceEigen(10,p2,p3,gx)
    sm = div(em,es)
    print "C2s time:"
    print (time.time()-start)

    writeImage(smfile,sm)
  else:
    sm = readImage3D(smfile)
  sm = pow(sm,8)
  plot3(gx,sub(1,sm),cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
        clab="1-coherence",png="sm")
def goPlanar():
  gx = readImage3D(gxfile)
  if not plotOnly:
    lof = LocalOrientFilter(4,1,1)
    u1 = zerofloat(n1,n2,n3)
    u2 = zerofloat(n1,n2,n3)
    u3 = zerofloat(n1,n2,n3)
    ep = zerofloat(n1,n2,n3)
    start=time.time()
    lof.applyForNormalPlanar(gx,u1,u2,u3,ep)
    print "C2 time:"
    print (time.time()-start)
    writeImage(epfile,ep)
  else:
    ep = readImage3D(epfile)
  plot3(gx)
  ep = pow(ep,8)
  plot3(gx,sub(1,ep),cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="1-planarity",png="ep")

def goStructureOrientedSemblance():
  sigma1,sigma2 = 8,2
  gx = readImage3D(gxfile)
  if not plotOnly:
    lof = LocalOrientFilter(sigma1,sigma2,sigma2)
    ets = lof.applyForTensors(gx)
    lsf = LocalSemblanceFilter(2,16)
    start = time.time()
    sms = lsf.semblance(LocalSemblanceFilter.Direction3.V,ets,gx)
    print "sos time:"
    print time.time()-start
    sms = pow(sms,8)
    writeImage(smsfile,sms)
  else:
    sms = readImage3D(smsfile)
  sms = pow(sms,8)
  plot3(gx,sub(1,sms),cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="1-semblance",png="sms") 

def goStructureOrientedPlanarity():
  sigma1,sigma2 = 8,2
  gx = readImage3D(gxfile)
  if not plotOnly:
    eps = zerofloat(n1,n2,n3)
    lof = LocalOrientFilter(sigma1,sigma2,sigma2)
    ets = lof.applyForTensors(gx)
    sta = StructureTensorAttribute(ets,16)
    sta.setEigenvalues(1.0,0.01,0.6)
    start=time.time()
    sta.applyForPlanar(gx,eps)
    print "sop time:"
    print time.time()-start
    writeImage(epsfile,eps)
  else:
    eps = readImage3D(epsfile)
  eps = pow(eps,8)
  plot3(gx,sub(1,eps),cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="1-planarity",png="eps") 

def goFaultLikelihoodScan():
  minPhi,maxPhi = 270,360
  minTheta,maxTheta = 65,85
  sigmaPhi,sigmaTheta = 12,20
  gx = readImage3D(gxfile)
  sigma1,sigma2,sigma3,pmax = 16.0,1.0,1.0,5.0
  p2,p3,ep = FaultScanner.slopes(sigma1,sigma2,sigma3,pmax,gx)
  gx = FaultScanner.taper(10,0,0,gx)
  fs = FaultScanner(sigmaPhi,sigmaTheta)
  fss = fs.scanForAllSemblance(minPhi,maxPhi,minTheta,maxTheta,p2,p3,gx)
  np = len(fss)
  nt = len(fss[0])
  sp = fs.makePhiSampling(minPhi,maxPhi)
  st = fs.makeThetaSampling(minTheta,maxTheta)
  for ip in range(np):
    pi = sp.getValue(ip)
    for it in range(nt):
      ti = sp.getValue(it)
      plot3(gx,fss[ip][it],cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="Fault likelihood",png="fl"+str(pi)+"-"+str(ti))

def goFaultLikelihood():
  minPhi,maxPhi = 0,360
  minTheta,maxTheta = 65,85
  sigmaPhi,sigmaTheta = 12,20
  gx = readImage3D(gxfile)
  if not plotOnly:
    sigma1,sigma2,sigma3,pmax = 16.0,1.0,1.0,5.0
    p2,p3,ep = FaultScanner.slopes(sigma1,sigma2,sigma3,pmax,gx)
    gx = FaultScanner.taper(10,0,0,gx)
    fs = FaultScanner(sigmaPhi,sigmaTheta)
    start = time.time()
    fl,fp,ft = fs.scan(minPhi,maxPhi,minTheta,maxTheta,p2,p3,gx)
    print "fault likelihood scan time:"
    print time.time()-start
    print "fl min =",min(fl)," max =",max(fl)
    print "fp min =",min(fp)," max =",max(fp)
    print "ft min =",min(ft)," max =",max(ft)
    writeImage(flfile,fl)
    writeImage(fpfile,fp)
    writeImage(ftfile,ft)
  else:
    fl = readImage3D(flfile)
    fp = readImage3D(fpfile)
    ft = readImage3D(ftfile)
  fs = FaultSkinner()
  cells = fs.findCells([fl,fp,ft])
  flt = zerofloat(n1,n2,n3)
  FaultCell.getFlThick(0,cells,flt)
  plot3(gx,fl,cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="Fault likelihood",png="fl")
  plot3(gx,fp,cmin=0,cmax=360,cmap=hueFill(1.0),
      clab="Fault strike (degrees)",cint=45,png="fp")
  plot3(gx,convertDips(ft),cmin=15,cmax=55,cmap=jetFill(1.0),
      clab="Fault dip (degrees)",png="ft")
  plot3(gx,flt,cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="Fault likelihood",png="flt")

def goFaultOrientScan():
  gx = readImage3D(gxfile)
  ep = readImage3D(epfile)
  fos = FaultOrientScanner3(sigmaPhi,sigmaTheta)
  if not plotOnly:
    fe,fp,ft = fos.scan(minPhi,maxPhi,minTheta,maxTheta,ep)
    fet,fpt,ftt=fos.thin([fe,fp,ft])
    writeImage(fefile,fe)
    writeImage(fetfile,fet)
    writeImage(fptfile,fpt)
    writeImage(fttfile,ftt)
  else:
    fe = readImage3D(fefile)
    fp = readImage3D(fpfile)
  print min(fe) 
  print max(fe) 
  ep = sub(1,pow(ep,8))
  plot3(gx,ep,cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="Planarity",png="ep")
  plot3(gx,fe,cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="Ray tracing",png="fl")
  plot3(gx,fp,cmin=1,cmax=360,cmap=jetFill(1.0),
      clab="Fault strike (degrees)",png="ph")

def goSurfaceVoting():
  gx = readImage3D(gxfile)
  osv = OptimalSurfaceVoterP(10,20,30)
  if not plotOnly:
    fet = readImage3D(fetfile)
    fpt = readImage3D(fptfile)
    ftt = readImage3D(fttfile)
    osv.setStrainMax(0.25,0.25)
    osv.setSurfaceSmoothing(2,2)
    start = time.time()
    fv,vp,vt = osv.applyVoting(4,0.3,fet,fpt,ftt)
    print "surface voting time:"
    print time.time()-start
    writeImage("vp",vp)
    writeImage("vt",vt)
    writeImage(fvfile,fv)
  else:
    fv = readImage3D(fvfile)
    vp = readImage3D(vpfile)
    vt = readImage3D(vtfile)
  '''
  plot3(gx,ep,cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="Planarity",png="ep")
  '''
  plot3(gx,fv,cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="Surface voting",png="fv")
  plot3(gx,fvp,cmin=1,cmax=180,cmap=jetFill(1.0),
      clab="Fault strike (degrees)",png="ph")

def goFaultSurfaces():
  gx = readImage3D(gxfile)
  if not plotOnly:
    osv = OptimalSurfaceVoterP(10,20,30)
    fv = readImage3D(fvfile)
    vp = readImage3D(vpfile)
    vt = readImage3D(vtfile)
    u1 = zerofloat(n1,n2,n3)
    u2 = zerofloat(n1,n2,n3)
    u3 = zerofloat(n1,n2,n3)
    ep = zerofloat(n1,n2,n3)
    lof = LocalOrientFilter(4,2,2)
    lof.applyForNormalPlanar(fv,u1,u2,u3,ep)
    ft,pt,tt = osv.thin([fv,vp,vt])
    fsk = FaultSkinner()
    fsk.setGrowing(10,0.3)
    seeds = fsk.findSeeds(10,0.8,ep,ft,pt,tt)
    skins = fsk.findSkins(0.65,2000,seeds,fv,vp,vt)
    sks = []
    for skin in skins:
      skin.smooth(5)
      if(skin.getX1max()>80):
        sks.append(skin)
    removeAllSkinFiles(fskfile)
    writeSkins(fskfile,sks)
  else:
    fv = readImage3D(fvfile)
    sks = readSkins(fskfile)
  for skin in sks:
    skin.updateStrike()
  plot3(gx,clab="Amplitude",png="seis")
  plot3(gx,fv,cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="Voting score",png="fv")
  plot3(gx,fv,cmin=0.0,cmax=180,cmap=hueFill(1.0),
      clab="Fault strike",png="fp")
  plot3(gx,skins=sks)
  plot3(gx,skinx=sks,au=80,ev=55,v3=0.05,png="skinv")

def goFaultSkins():
  print "goSkin ..."
  lowerLikelihood = 0.5
  upperLikelihood = 0.8
  minSkinSize = 2000
  gx = readImage3D(gxfile)
  fl = readImage3D(flfile)
  fp = readImage3D(fpfile)
  ft = readImage3D(ftfile)
  fs = FaultSkinner()
  fs.setGrowLikelihoods(lowerLikelihood,upperLikelihood)
  fs.setMinSkinSize(minSkinSize)
  cells = fs.findCells([fl,fp,ft])
  skins = fs.findSkins(cells)
  sks = []
  for skin in skins:
    skin.smoothCellNormals(4)
    if(skin.getX1max()>80):
      sks.append(skin)
  print "total number of cells =",len(cells)
  print "total number of skins =",len(skins)
  print "number of cells in skins =",FaultSkin.countCells(skins)
  plot3(gx,skinx=sks,au=80,ev=55,v3=0.05,png="skind")

# for displaying only
def goVoters():
  gx = readImage3D(gxfile)
  ep = readImage3D(epfile)
  ft = readImage3D(fetfile)
  pt = readImage3D(fptfile)
  tt = readImage3D(fttfile)
  ep = pow(ep,8)
  os = OptimalSurfacer(10,20,20)
  os.setStrainMax(0.25,0.25)
  os.setAttributeSmoothing(1)
  os.setSurfaceSmoothing(2,1)
  sds = os.pickSeeds(79,15,35,0.5,ft,pt,tt)
  tgs1 = []
  tgs2 = []
  tgs3 = []
  for cell in sds:
    c1 = cell.getI1();
    c2 = cell.getI2();
    c3 = cell.getI3();
    u = cell.getFaultNormal();
    v = cell.getFaultDipVector();
    w = cell.getFaultStrikeVector();
    gb = os.getUvwBox(c1,c2,c3,u,v,w,gx)
    eb = os.getUvwBox(c1,c2,c3,u,v,w,ep)
    sf = os.findSurface(20,30,30,eb)
    xyz1 = os.getSurfaceTriangles(c1,c2,c3,u,v,w,sf)
    tg1 = TriangleGroup(True,xyz1)
    tg1.setColor(Color.CYAN)
    tgs1.append(tg1)
    xyz2,rgb2 = os.getSurfaceTriangles(False,c1,c2,c3,0.25,1.0,u,v,w,sf,sub(1,ep))
    xyz3,rgb3 = os.getSurfaceTriangles(True,c1,c2,c3,0.25,1.0,u,v,w,sf,sub(1,ep))
    tg2 = TriangleGroup(True,xyz2,rgb2)
    tg3 = TriangleGroup(True,xyz3,rgb3)
    tgs2.append(tg2)
    tgs3.append(tg3)
  plot3(gx,sub(1,ep),tgs=tgs1,cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="1-planarity",png="vs")
  plot3(gx,sub(1,ep),tgs=tgs2,cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="1-planarity",png="vsep")
  plot3(gx,tgs=tgs3, png="vss")

def gain(x):
  g = mul(x,x) 
  ref = RecursiveExponentialFilter(10.0)
  ref.apply1(g,g)
  y = zerofloat(n1,n2,n3)
  div(x,sqrt(g),y)
  return y

def smooth(sig,u):
  v = copy(u)
  rgf = RecursiveGaussianFilterP(sig)
  rgf.apply0(u,v)
  return v

def smooth2(sig1,sig2,u):
  v = copy(u)
  rgf1 = RecursiveGaussianFilterP(sig1)
  rgf2 = RecursiveGaussianFilterP(sig2)
  rgf1.apply0X(u,v)
  rgf2.applyX0(v,v)
  return v


def normalize(e):
  emin = min(e)
  emax = max(e)
  return mul(sub(e,emin),1.0/(emax-emin))

#############################################################################
# graphics

def jetFill(alpha):
  return ColorMap.setAlpha(ColorMap.JET,alpha)
def jetFillExceptMin(alpha):
  a = fillfloat(alpha,256)
  a[0] = 0.0
  return ColorMap.setAlpha(ColorMap.JET,a)
def jetRamp(alpha):
  return ColorMap.setAlpha(ColorMap.JET,rampfloat(0.0,alpha/256,256))
def bwrFill(alpha):
  return ColorMap.setAlpha(ColorMap.BLUE_WHITE_RED,alpha)
def bwrNotch(alpha):
  a = zerofloat(256)
  for i in range(len(a)):
    if i<128:
      a[i] = alpha*(128.0-i)/128.0
    else:
      a[i] = alpha*(i-127.0)/128.0
  return ColorMap.setAlpha(ColorMap.BLUE_WHITE_RED,a)
def hueFill(alpha):
  return ColorMap.getHue(0.0,1.0,alpha)
def hueFillExceptMin(alpha):
  a = fillfloat(alpha,256)
  a[0] = 0.0
  return ColorMap.setAlpha(ColorMap.getHue(0.0,1.0),a)

def addColorBar(frame,clab=None,cint=None):
  cbar = ColorBar(clab)
  if cint:
    cbar.setInterval(cint)
  cbar.setFont(Font("Arial",Font.PLAIN,32)) # size by experimenting
  cbar.setWidthMinimum
  cbar.setBackground(Color.WHITE)
  frame.add(cbar,BorderLayout.EAST)
  return cbar

def convertDips(ft):
  return FaultScanner.convertDips(0.2,ft) # 5:1 vertical exaggeration

def plot3(f,g=None,fbs=None,cmin=-2,cmax=2,cmap=None,clab=None,cint=None,
          sx=None,sy=None,surf=None,tgs=None,fd=None,cells=None,
          skins=None,skinx=None,au=45,ev=36,v3=-0.05,smax=0,links=False,png=None):
  n3 = len(f)
  n2 = len(f[0])
  n1 = len(f[0][0])
  s1,s2,s3=Sampling(n1),Sampling(n2),Sampling(n3)
  d1,d2,d3 = s1.delta,s2.delta,s3.delta
  f1,f2,f3 = s1.first,s2.first,s3.first
  l1,l2,l3 = s1.last,s2.last,s3.last
  sf = SimpleFrame(AxesOrientation.XRIGHT_YOUT_ZDOWN)
  cbar = None
  if g==None:
    ipg = sf.addImagePanels(s1,s2,s3,f)
    if cmap!=None:
      ipg.setColorModel(cmap)
    if cmin!=None and cmax!=None:
      ipg.setClips(cmin,cmax)
    else:
      ipg.setClips(-2.0,2.0)
    if clab:
      cbar = addColorBar(sf,clab,cint)
      ipg.addColorMapListener(cbar)
  else:
    ipg = ImagePanelGroup2(s1,s2,s3,f,g)
    ipg.setClips1(-2,2)
    if cmin!=None and cmax!=None:
      ipg.setClips2(cmin,cmax)
    if cmap==None:
      cmap = jetFill(0.8)
    ipg.setColorModel2(cmap)
    if clab:
      cbar = addColorBar(sf,clab,cint)
      ipg.addColorMap2Listener(cbar)
    sf.world.addChild(ipg)
  if cbar:
    cbar.setWidthMinimum(120)
  if fbs:
    mc = MarchingCubes(s1,s2,s3,fbs)
    ct = mc.getContour(0.0)
    tg = TriangleGroup(ct.i,ct.x,ct.u)
    states = StateSet()
    cs = ColorState()
    cs.setColor(Color.MAGENTA)
    states.add(cs)
    lms = LightModelState()
    lms.setTwoSide(True)
    states.add(lms)
    ms = MaterialState()
    ms.setColorMaterial(GL_AMBIENT_AND_DIFFUSE)
    ms.setSpecular(Color.WHITE)
    ms.setShininess(100.0)
    states.add(ms)
    tg.setStates(states);
    sf.world.addChild(tg)
  if cells:
    ss = StateSet()
    lms = LightModelState()
    lms.setTwoSide(True)
    ss.add(lms)
    ms = MaterialState()
    ms.setSpecular(Color.GRAY)
    ms.setShininess(100.0)
    ms.setColorMaterial(GL_AMBIENT_AND_DIFFUSE)
    ms.setEmissiveBack(Color(0.0,0.0,0.5))
    ss.add(ms)
    cmap = ColorMap(0.0,1.0,ColorMap.JET)
    xyz,uvw,rgb = FaultCell.getXyzUvwRgbForLikelihood(0.7,cmap,cells,False)
    qg = QuadGroup(xyz,uvw,rgb)
    qg.setStates(ss)
    sf.world.addChild(qg)
  if tgs:
    for tg in tgs:
      sf.world.addChild(tg)
  if surf:
    tg = TriangleGroup(True,surf)
    sf.world.addChild(tg)
  if skinx:
    sg = Group()
    ss = StateSet()
    lms = LightModelState()
    #lms.setTwoSide(False)
    lms.setTwoSide(False)
    ss.add(lms)
    ms = MaterialState()
    ms.setSpecular(Color.GRAY)
    ms.setShininess(100.0)
    ms.setColorMaterial(GL_AMBIENT_AND_DIFFUSE)
    if not smax:
      ms.setEmissiveBack(Color(0.0,0.0,0.0))
    ss.add(ms)
    sg.setStates(ss)
    for skin in skinx:
      #cmap = ColorMap(0.0,1.0,ColorMap.JET)
      cmap = ColorMap(0.0,180,hueFill(1.0))
      #tg = skin.getTriMesh(cmap)
      #tg = skin.getTriMeshStrike(cmap)
      qg = skin.getQuadMeshStrike(cmap)
      sg.addChild(qg)
    sf.world.addChild(sg)
  if skins:
    sg = Group()
    ss = StateSet()
    lms = LightModelState()
    #lms.setTwoSide(True)
    lms.setTwoSide(False)
    ss.add(lms)
    ms = MaterialState()
    ms.setSpecular(Color.GRAY)
    ms.setShininess(100.0)
    ms.setColorMaterial(GL_AMBIENT_AND_DIFFUSE)
    if not smax:
      ms.setEmissiveBack(Color(0.0,0.0,0.5))
    ss.add(ms)
    sg.setStates(ss)
    size = 2.0
    if links:
      size = 0.5 
    for skin in skins:
      if smax>0.0: # show fault throws
        cmap = ColorMap(0.0,smax,ColorMap.JET)
        xyz,uvw,rgb = skin.getCellXyzUvwRgbForThrow(size,cmap,False)
      else: # show fault likelihood
        cmap = ColorMap(0.25,1.0,ColorMap.JET)
        xyz,uvw,rgb = skin.getCellXyzUvwRgbForLikelihood(size,cmap,False)
      qg = QuadGroup(xyz,uvw,rgb)
      qg.setStates(None)
      sg.addChild(qg)
      if links:
        xyz = skin.getCellLinksXyz()
        lg = LineGroup(xyz)
        sg.addChild(lg)
    sf.world.addChild(sg)
  ipg.setSlices(106,80,207)
  ipg.setSlices(93,25,32)
  #ipg.setSlices(115,25,167)
  if cbar:
    sf.setSize(987,720)
  else:
    sf.setSize(850,720)
  vc = sf.getViewCanvas()
  vc.setBackground(Color.WHITE)
  radius = 0.5*sqrt(n1*n1+n2*n2+n3*n3)
  ov = sf.getOrbitView()
  zscale = 0.3*max(n2*d2,n3*d3)/(n1*d1)
  ov.setAxesScale(1.0,1.0,zscale)
  ov.setScale(1.55)
  ov.setWorldSphere(BoundingSphere(BoundingBox(f3,f2,f1,l3,l2,l1)))
  ov.setTranslate(Vector3(0.0,0.06,v3))
  ov.setAzimuthAndElevation(au,ev)
  sf.setVisible(True)
  if png and pngDir:
    sf.paintToFile(pngDir+png+".png")
    if cbar:
      cbar.paintToPng(720,1,pngDir+png+"cbar.png")
#############################################################################
# Run the function main on the Swing thread
import sys
class _RunMain(Runnable):
  def __init__(self,main):
    self.main = main
  def run(self):
    self.main(sys.argv)
def run(main):
  SwingUtilities.invokeLater(_RunMain(main)) 
run(main)
