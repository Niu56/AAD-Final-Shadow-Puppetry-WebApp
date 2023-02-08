# Import javascript modules
from js import THREE, window, document, Object, console
# Import pyscript / pyodide modules
from pyodide.ffi import create_proxy, to_js
# Import python module
import math
import random
import time
from random import seed
# Import NumPy as np
import numpy as np


#-----------------------------------------------------------------------
# USE THIS FUNCTION TO WRITE THE MAIN PROGRAM
def main():
    #-----------------------------------------------------------------------
    # VISUAL SETUP
    # Declare the variables
    global renderer, scene, camera, controls,composer
    
    #Set up the renderer
    renderer = THREE.WebGLRenderer.new()
    renderer.setPixelRatio( window.devicePixelRatio )
    renderer.setSize(window.innerWidth, window.innerHeight)
    document.body.appendChild(renderer.domElement)
    
    renderer.shadowMap.enabled = True
    renderer.shadowMap.type = THREE.PCFSoftShadowMap

    # Set up the scene
    scene = THREE.Scene.new()
    back_color = THREE.Color.new(0.1,0.1,0.1)
    scene.background = back_color
    camera = THREE.PerspectiveCamera.new(75, window.innerWidth/window.innerHeight, 0.1, 10000)
    camera.position.z = 200
    camera.position.y = 50
    camera.position.x = -150
    scene.add(camera)

    # Set up the sun
    global material
    color = THREE.Color.new(0.95,0.5,0.15)
    material = THREE.MeshBasicMaterial.new()
    material.transparent = False
    material.opacity = 0.8
    material.color = color

    global sphere, sphere_mesh, edges, sphere_line, sun
    sun = THREE.Object3D.new()
    sphere = THREE.SphereGeometry.new(15,32,16)
    sphere_mesh = THREE.Mesh.new(sphere, material)
    sphere_mesh.position.set(0,0,0)
    sun.add(sphere_mesh)
    edges = THREE.EdgesGeometry.new(sphere)
    edges_material = THREE.MeshBasicMaterial.new()
    edges_color = THREE.Color.new(1,1,1)
    edges_material.color = edges_color
    sphere_line = THREE.LineSegments.new( edges, edges_material )
    sphere_line.position.set(0,0,0)
    sun.add(sphere_line)

    #Light set up parameters

    global light
    light = THREE.DirectionalLight.new(0xffffff, 0.6)
    light.color.setHSL( 0.1, 1, 0.95 )
    light.position.set( 0, 100, 0 )
    light.castShadow = True
    scene.add(light)
    d = 300
    light.shadow.camera.left = -d
    light.shadow.camera.right = d
    light.shadow.camera.top = d
    light.shadow.camera.bottom = -d
    light.shadow.camera.near = 20
    light.shadow.camera.far = 8000
    light.shadow.mapSize.x = 2048
    light.shadow.mapSize.y = 2048

    scene.add(sun)

    InsideLight = THREE.PointLight.new(0xffffff, 0.4)
    InsideLight.color.setHSL( 0.1, 1, 0.95 )
    InsideLight.position.set( -50, 50, 100)
    InsideLight.castShadow = True
    scene.add(InsideLight)

    InsideLight.shadow.camera.left = -d
    InsideLight.shadow.camera.right = d
    InsideLight.shadow.camera.top = d
    InsideLight.shadow.camera.bottom = -d
    InsideLight.shadow.camera.near = 20
    InsideLight.shadow.camera.far = 8000
    InsideLight.shadow.mapSize.x = 2048
    InsideLight.shadow.mapSize.y = 2048


    # Set ut the orbit

    global curve, points, orbit, orbit_material, orbit_geom
    Size = 500
    curve= THREE.CubicBezierCurve3.new(THREE.Vector3.new(-Size, 0, -Size), THREE.Vector3.new(-Size, 2* Size, -Size), THREE.Vector3.new(Size, 2* Size, Size), THREE.Vector3.new(Size, 0, Size))

    points = curve.getPoints( 50 )
    orbit_geom = THREE.BufferGeometry.new().setFromPoints( points )
    orbit_material = THREE.MeshBasicMaterial.new()
    orbit_color = THREE.Color.new(0.6,0.3,0.1)
    orbit_material.color = orbit_color
    orbit = THREE.Line.new( orbit_geom, orbit_material )
    scene.add(orbit)

    #states = ['Random with seed', 'Changing with time']

    # Graphic Post Processing
    global composer
    post_process()

    # Set up responsive window
    resize_proxy = create_proxy(on_window_resize)
    window.addEventListener('resize', resize_proxy) 
    #-----------------------------------------------------------------------
    # YOUR DESIGN / GEOMETRY GENERATION
    # Geometry Creation

    global NbPt, Tps

    NbPt = {"value" : 20}
    NbPt = Object.fromEntries(to_js(NbPt))
    Tps = {"value" : 0}
    Tps = Object.fromEntries(to_js(Tps))


    #Code from Lars Neumann
    global SquareShapeLines, InsideShapeLines
    global InsideShapePoints
    global BSp1, BSp2, BSp3, BSp4, RandomPoints

    BSp1 = np.array([0,0,0])
    BSp2 = np.array([0,100,0])
    BSp3 = np.array([50,100,0])
    BSp4 = np.array([50,0,0])

    SquareShapePoints = [BSp1,BSp2,BSp3,BSp4]

    SquareShapeLines = []
    for i in range(len(SquareShapePoints)):
        if i < len(SquareShapePoints)-1:
            CurrentLine = [SquareShapePoints[i], SquareShapePoints[i+1]]
            SquareShapeLines.append(CurrentLine)
        else:
            CurrentLine = [SquareShapePoints[i], SquareShapePoints[i-(len(SquareShapePoints)-1)]]
            SquareShapeLines.append(CurrentLine)

    #Transferring NumPy-Lines into Three.js for visualization
    ThreeCurrentLine = []
    ThreeLinesBaseSquare = []

        #Base square
    for i in SquareShapeLines:
        for j in i:
            TempArrayToList = j.tolist()
            ThreeVec1 = THREE.Vector2.new(TempArrayToList[0],TempArrayToList[1])
            ThreeCurrentLine.append(ThreeVec1)
        ThreeLinesBaseSquare.append (ThreeCurrentLine)
        ThreeCurrentLine = []     

    draw_system_baseshape(ThreeLinesBaseSquare)   
    #End Code from Lars Neumann

            
    InsideShapePoints = [BSp1,BSp2,BSp3,BSp4]
    for i in range(NbPt.value):
        RandomPoints = np.array([random.randrange(0,50),random.randrange(0,100),0])
        InsideShapePoints.append(RandomPoints)

    InsideShapeLines = []
    for pt in InsideShapePoints:
        for other in InsideShapePoints:
            if other is not pt:
                dist = np.linalg.norm(pt-other)
                if dist < 50:
                    CurrentLine = [pt, other]
                    InsideShapeLines.append(CurrentLine)
    

    ThreeLinesInside = []

    #Inside lines
    for i in InsideShapeLines:
        for j in i:
            TempArrayToList = j.tolist()
            ThreeVec2 = THREE.Vector2.new(TempArrayToList[0],TempArrayToList[1])
            ThreeCurrentLine.append(ThreeVec2)
        ThreeLinesInside.append (ThreeCurrentLine)
        ThreeCurrentLine = []


    draw_system_baseshape(ThreeLinesInside)

    planeGeometry1 = THREE.PlaneGeometry.new(200, 300)
    planeMaterial = THREE.MeshStandardMaterial.new({ 1, 1, 1 })
    MurFenetre1 = THREE.Mesh.new( planeGeometry1, planeMaterial)
    planeGeometry1.translate(-300,50,-100)
    MurFenetre1.shadowSide = THREE.DoubleSide
    MurFenetre1.receiveShadow = True
    MurFenetre1.castShadow = True
    scene.add(MurFenetre1)

    planeGeometry1 = THREE.PlaneGeometry.new(200, 300)
    planeMaterial = THREE.MeshStandardMaterial.new({ 1, 1, 1 })
    MurFenetre2 = THREE.Mesh.new( planeGeometry1, planeMaterial)
    planeGeometry1.translate(200,50,-100)
    MurFenetre2.shadowSide = THREE.DoubleSide
    MurFenetre2.receiveShadow = True
    MurFenetre2.castShadow = True
    scene.add(MurFenetre2)

    planeGeometry4 = THREE.PlaneGeometry.new(300, 50)
    planeMaterial = THREE.MeshStandardMaterial.new({ 1, 1, 1 })
    MurFenetre3 = THREE.Mesh.new( planeGeometry4, planeMaterial)
    planeGeometry4.translate(-50,-75,-100)
    MurFenetre3.shadowSide = THREE.DoubleSide
    MurFenetre3.receiveShadow = True
    MurFenetre3.castShadow = True
    scene.add(MurFenetre3)

    planeGeometry5 = THREE.PlaneGeometry.new(400, 50)
    planeMaterial = THREE.MeshStandardMaterial.new({ 1, 1, 1 })
    MurFenetre4 = THREE.Mesh.new( planeGeometry5, planeMaterial)
    planeGeometry5.translate(-100,175,-100)
    MurFenetre4.shadowSide = THREE.DoubleSide
    MurFenetre4.receiveShadow = True
    MurFenetre4.castShadow = True
    scene.add(MurFenetre4)

    planeGeometry2 = THREE.PlaneGeometry.new(5000, 5000)
    planeMaterial = THREE.MeshStandardMaterial.new({ 1, 1, 1 })
    plane2 = THREE.Mesh.new( planeGeometry2, planeMaterial)
    planeGeometry2.rotateX(math.radians(-90))
    planeGeometry2.translate(0,-100,-50)
    plane2.receiveShadow = True
    scene.add(plane2)

    planeGeometry3 = THREE.PlaneGeometry.new(5000, 1000)
    planeMaterial = THREE.MeshStandardMaterial.new({ 1, 1, 1 })
    plane3 = THREE.Mesh.new( planeGeometry3, planeMaterial)
    planeGeometry3.rotateX(math.radians(-90))
    planeGeometry3.translate(0,200,400)
    plane3.material.side = THREE.DoubleSide
    plane3.shadowSide = THREE.DoubleSide
    plane3.castShadow = True
    plane3.receiveShadow = False
    scene.add(plane3)
    
    planeGeometry7 = THREE.PlaneGeometry.new(500, 300)
    planeMaterial = THREE.MeshStandardMaterial.new({ 1, 1, 1 })
    plane7 = THREE.Mesh.new( planeGeometry7, planeMaterial)
    plane7.material.side = THREE.DoubleSide
    plane7.shadowSide = THREE.DoubleSide
    planeGeometry7.rotateY(math.radians(-90))
    planeGeometry7.translate(200,50,150)
    plane7.receiveShadow = True
    plane7.castShadow = False
    scene.add(plane7)

    skygeometry = THREE.SphereGeometry.new(1000 ,32 ,16)
    skymaterial = THREE.MeshBasicMaterial.new()
    skycolor = THREE.Color.new(153/255, 255, 255)
    skymaterial.color = skycolor
    skysphere = THREE.Mesh.new(skygeometry,skymaterial)
    skysphere.material.side = THREE.BackSide
    scene.add(skysphere)

    window.requestAnimationFrame(create_proxy(render))

    #-----------------------------------------------------------------------
    # USER INTERFACE
    # Set up Mouse orbit control
    controls = THREE.OrbitControls.new(camera, renderer.domElement)
    controls.rotateSpeed = 0
    controls.panSpeed = 0.2

    def createLimitPan(camera, controls, THREE ):
        v = THREE.Vector3.new()
        minPan = THREE.Vector3.new()
        maxPan = THREE.Vector3.new()

        maxX = 20
        minX = -20
        maxZ = 20
        minZ = -20

        minPan.set(minX, -20, minZ)
        maxPan.set(maxX, 20, maxZ)
        v.copy(controls.target)
        controls.target.clamp(minPan, maxPan)
        v.sub(controls.target)
        camera.position.sub(v)

    createLimitPan(camera, controls, THREE)
    

    # Set up GUI
    gui = window.dat.GUI.new()
    param_folder = gui.addFolder('Number of points')
    param_folder.add(NbPt, "value", 0, 100, 1)
    time_folder = gui.addFolder('Time of the day')
    time_folder.add(Tps, "value", 0, 0.5,0.1)
    time_folder.open()
    
    #-----------------------------------------------------------------------
    # RENDER + UPDATE THE SCENE AND GEOMETRIES
    render()
    
#-----------------------------------------------------------------------
# HELPER FUNCTIONS

#Turning the generated point-list into a drawn line

def draw_system_baseshape(lines):
    for points in lines:
        for i in range(6):
            for j in range(2):
                global vis_line

                line_geom = THREE.BufferGeometry.new()
                points = to_js(points)
                
                line_geom.setFromPoints( points )

                material = THREE.LineBasicMaterial.new()
                material.color = THREE.Color.new(1,1,1)
                
                vis_line = THREE.Line.new( line_geom, material )
                global scene

                line_geom.translate(-200,-50,-100)

                line_geom.translate(50*i,100*j,0)

                vis_line.castShadow = True
                vis_line.receiveShadow = False

                scene.add(vis_line)

def update_random():
    global SquareShapeLines, InsideShapeLines, ThreeLinesInside
    global InsideShapePoints
    global BSp1, BSp2, BSp3, BSp4, RandomPoints
    if len(InsideShapePoints) != 0:
        if len(InsideShapePoints) != NbPt.value:  
        

            InsideShapePoints = [BSp1,BSp2,BSp3,BSp4]

            for i in range(NbPt.value):
                RandomPoints = np.array([random.randrange(0,50),random.randrange(0,100),0])
                InsideShapePoints.append(RandomPoints)

            InsideShapeLines = []
            for pt in InsideShapePoints:
                for other in InsideShapePoints:
                    if other is not pt:
                        dist = np.linalg.norm(pt-other)
                        if dist < 50:
                            CurrentLine = [pt, other]
                            InsideShapeLines.append(CurrentLine)

            ThreeCurrentLine = []
            ThreeLinesInside = []

            for i in InsideShapeLines:
                for j in i:
                    TempArrayToList = j.tolist()
                    ThreeVec2 = THREE.Vector2.new(TempArrayToList[0],TempArrayToList[1])
                    ThreeCurrentLine.append(ThreeVec2)
                ThreeLinesInside.append (ThreeCurrentLine)
                ThreeCurrentLine = []

            
            draw_system_baseshape(ThreeLinesInside)
            scene.remove(vis_line)
            

    


# move the sun along the orbit
def changePosition():
    global position
    position = curve.getPointAt(Tps.value)
    sun.position.copy(position)
    light.position.copy(position)
    
# set orientation of the sun 
def changeLookAt():
    tangent = curve.getTangentAt(Tps.value)
    lookAtVec = tangent.add(position)
    sun.lookAt(lookAtVec)

def render(*args):
    
    #loopTime = 10 * 1000
    #move_time = int(time.time() * 500)
    #t = (move_time % loopTime) / loopTime

    changePosition()
    changeLookAt()


    if len(InsideShapeLines) < NbPt.value:
        update_random()        

    window.requestAnimationFrame(create_proxy(render))
    
    controls.update()
    composer.render()


# Graphical post-processing
def post_process():
    render_pass = THREE.RenderPass.new(scene, camera)
    render_pass.clearColor = THREE.Color.new(0,0,0)
    render_pass.ClearAlpha = 0
    fxaa_pass = THREE.ShaderPass.new(THREE.FXAAShader)

    pixelRatio = window.devicePixelRatio

    fxaa_pass.material.uniforms.resolution.value.x = 1 / ( window.innerWidth * pixelRatio )
    fxaa_pass.material.uniforms.resolution.value.y = 1 / ( window.innerHeight * pixelRatio )
   
    global composer
    composer = THREE.EffectComposer.new(renderer)
    composer.addPass(render_pass)
    composer.addPass(fxaa_pass)

# Adjust display when window size changes
def on_window_resize(event):

    event.preventDefault()

    global renderer
    global camera
    
    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()

    renderer.setSize( window.innerWidth, window.innerHeight )

    #post processing after resize
    post_process()
#-----------------------------------------------------------------------
#RUN THE MAIN PROGRAM
if __name__=='__main__':
    main()