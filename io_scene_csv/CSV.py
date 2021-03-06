#-------------------------------------------------------------------------------
#
#       CSV model loader
#       RGUPS, Virtual Railway 11/07/2018
#       Developer: Dmirty Pritykin
#
#-------------------------------------------------------------------------------
import math

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class CSVmesh:

    def __init__(self):
        self.name = ""
        self.vertex_list = []
        self.normals_list = []
        self.vertex_indices = []
        self.faces_list = []
        self.texcoords_list = []
        self.texture_file = ""
        self.diffuse_color = []
        self.decale_color = []
        self.is_decale = False
        self.is_addFace2 = False
        self.ty_max = 1

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class CSVLoader:

    meshes_list = []

    def __init__(self):
        self.meshes_list.clear()

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def parseLine(self, line):
        tmp = line.rstrip('\n').rstrip('\r').split(",")

        for i, token in enumerate(tmp):
            str = token.strip(' ')
            tmp[i] = str

        return tmp

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def addFace(self, command, mesh, is_face2 = False):
        face = []
        for i in range(1, len(command)):
            try:
                v = int(command[i])
                face.append(v)
            except ValueError:
                pass

        b_face = []
        b_face.append(face[0])

        # Invert vertices order
        for i in range(len(face)-1, 0, -1):
            b_face.append(face[i])

        mesh.faces_list.append(tuple(b_face))
        mesh.is_addFace2 = is_face2

        #if is_face2:
            #mesh.faces_list.append(tuple(face))

    # ---------------------------------------------------------------------------
    #
    # ---------------------------------------------------------------------------
    def createCube(self, command, mesh):

        x = 0
        y = 0
        z = 0

        try:
            x = float(command[1])
            y = float(command[2])
            z = float(command[3])
        except Exception as ex:
            print(ex)
            return

        # Add vertices
        v = (x, y, -z)
        mesh.vertex_list.append(v)
        v = (x, -y, -z)
        mesh.vertex_list.append(v)
        v = (-x, -y, -z)
        mesh.vertex_list.append(v)
        v = (-x, y, -z)
        mesh.vertex_list.append(v)
        v = (x, y, z)
        mesh.vertex_list.append(v)
        v = (x, -y, z)
        mesh.vertex_list.append(v)
        v = (-x, -y, z)
        mesh.vertex_list.append(v)
        v = (-x, y, z)
        mesh.vertex_list.append(v)

        # Add faces
        face = (0, 1, 2, 3)
        mesh.faces_list.append(face)
        face = (0, 4, 5, 1)
        mesh.faces_list.append(face)
        face = (0, 3, 7, 4)
        mesh.faces_list.append(face)
        face = (6, 5, 4, 7)
        mesh.faces_list.append(face)
        face = (6, 7, 3, 2)
        mesh.faces_list.append(face)
        face = (6, 2, 1, 5)
        mesh.faces_list.append(face)

    # ---------------------------------------------------------------------------
    #
    # ---------------------------------------------------------------------------
    def createCylinder(self, command, mesh):

        n = 0
        r1 = 0.0
        r2 = 0.0
        h = 0.0

        try:
            n = int(command[1])
            r1 = float(command[2])
            r2 = float(command[3])
            h = float(command[4])
        except Exception as ex:
            print(ex)
            return

        # Vertices generation
        for i in range(0, n):
            x = round(r1 * math.cos(2 * math.pi * i / n), 6)
            y = round(h / 2.0, 4)
            z = round(r1 * math.sin(2 * math.pi * i / n), 6)
            mesh.vertex_list.append((x, y, z))

            x = round(r2 * math.cos(2 * math.pi * i / n), 6)
            y = round(-h / 2.0, 4)
            z = round(r2 * math.sin(2 * math.pi * i / n), 6)
            mesh.vertex_list.append((x, y, z))

        # Side faces generation
        for i in range(0, n - 1):
            face = (2 * (i + 1), 2 * (i + 1) + 1, 2 * (i + 1) - 1, 2 * i)
            mesh.faces_list.append(face)

        mesh.faces_list.append((0, 1, 2 * n - 1, 2 * n - 2))

        # Lower face generation

        if r2 > 0:
            face = []
            for i in range(n-1, -1, -1):
                face.append(2*i)
            mesh.faces_list.append(tuple(face))

        # Upper face generation
        if r1 > 0:
            face = []
            for i in range(0, n):
                face.append(2*i + 1)
            mesh.faces_list.append(tuple(face))

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def Translate(self, command, mesh):

        try:
            x = float(command[1])
            y = float(command[2])
            z = float(command[3])
        except Exception as ex:
            print(ex)
            return

        for i, v in enumerate(mesh.vertex_list):
            tmp = list(v)
            tmp[0] = tmp[0] + x
            tmp[1] = tmp[1] + y
            tmp[2] = tmp[2] + z
            v = tuple(tmp)
            mesh.vertex_list[i] = v

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def TranslateAll(self, command, meshes_list, mesh):
        for m in meshes_list:
            self.Translate(command, m)

        self.Translate(command, mesh)


    # ---------------------------------------------------------------------------
    #
    # ---------------------------------------------------------------------------
    def Rotate(self, command, mesh):
        try:
            ux = float(command[1])
            uy = float(command[2])
            uz = float(command[3])
            angle = -float(command[4]) * math.pi / 180.0

            len = math.sqrt(ux * ux + uy * uy + uz * uz)

            try:

                # Normalize axis vector
                ex = ux / len
                ey = uy / len
                ez = uz / len

                # Rotate vertex by Rodrigue's formula
                for i, v in enumerate(mesh.vertex_list):
                    tmp = list(v)

                    c = ex * tmp[0] + ey * tmp[1] + ez * tmp[2]

                    nx = ez * tmp[1] - ey * tmp[2]
                    ny = ex * tmp[2] - ez * tmp[0]
                    nz = ey * tmp[0] - ex * tmp[1]

                    tmp[0] = round(c * (1 - math.cos(angle)) * ex + nx * math.sin(angle) + tmp[0] * math.cos(angle), 4)
                    tmp[1] = round(c * (1 - math.cos(angle)) * ey + ny * math.sin(angle) + tmp[1] * math.cos(angle), 4)
                    tmp[2] = round(c * (1 - math.cos(angle)) * ez + nz * math.sin(angle) + tmp[2] * math.cos(angle), 4)
                    v = tuple(tmp)
                    mesh.vertex_list[i] = v

            except Exception as ex:
                print(ex)
                return

        except Exception as ex:
            print(ex)
            return

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def RotateAll(self, command, meshes_list, mesh):
        for m in meshes_list:
            self.Rotate(command, m)

        self.Rotate(command, mesh)

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def Scale(self, command, mesh):
        try:
            sx = float(command[1])
            sy = float(command[2])
            sz = float(command[3])
        except Exception as ex:
            print(ex)
            return

        for i, v in enumerate(mesh.vertex_list):
            tmp = list(v)
            tmp[0] = sx * tmp[0]
            tmp[1] = sy * tmp[1]
            tmp[2] = sx * tmp[2]
            v = tuple(tmp)
            mesh.vertex_list[i] = v

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def ScaleAll(self, command, meshes_list, mesh):
        for m in meshes_list:
            self.Scale(command, m)

        self.Scale(command, mesh)

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def Mirror(self, command, mesh):
        try:
            mx = int(command[1])
            my = int(command[2])
            mz = int(command[3])
        except Exception as ex:
            print(ex)
            return

        for i, v in enumerate(mesh.vertex_list):
            tmp = list(v)

            if mx != 0:
                tmp[0] = -tmp[0]

            if my != 0:
                tmp[1] = -tmp[1]

            if mz != 0:
                tmp[2] = -tmp[2]

            v = tuple(tmp)
            mesh.vertex_list[i] = v

    # ---------------------------------------------------------------------------
    #
    # ---------------------------------------------------------------------------
    def MirrorAll(self, command, meshes_list, mesh):
        for m in meshes_list:
            self.Mirror(command, m)

        self.Mirror(command, mesh)

    # ---------------------------------------------------------------------------
    #
    # ---------------------------------------------------------------------------
    def Shear(self, command, mesh):
        try:
            dx = float(command[1])
            dy = float(command[2])
            dz = float(command[3])

            sx = float(command[4])
            sy = float(command[5])
            sz = float(command[6])

            r = float(command[7])
        except Exception as ex:
            print(ex)
            return

        # normalize vectors
        d_len = math.sqrt(dx * dx + dy * dy + dz * dz)

        if d_len == 0:
            return

        dx /= d_len
        dy /= d_len
        dz /= d_len

        s_len = math.sqrt(sx * sx + sy * sy + sz * sz)

        if s_len == 0:
            return

        sx /= s_len
        sy /= s_len
        sz /= s_len

        for i, v in enumerate(mesh.vertex_list):
            tmp = list(v)
            n = r * (dx * tmp[0] + dy * tmp[1] + dz * tmp[2])
            tmp[0] += sx * n;
            tmp[1] += sy * n;
            tmp[2] += sz * n;

            vertex = tuple(tmp)
            mesh.vertex_list[i] = vertex


    # ---------------------------------------------------------------------------
    #
    # ---------------------------------------------------------------------------
    def ShearAll(self, command, meshes_list, mesh):
        for m in meshes_list:
            self.Shear(command, m)

        self.Shear(command, mesh)

    # ---------------------------------------------------------------------------
    #
    # ---------------------------------------------------------------------------
    def toRightBasis(self, meshes_list):
        for m in meshes_list:
            command = [None, '0', '0', '1']
            self.Mirror(command, m)
            command = [None, '1', '0', '0', '90']
            self.Rotate(command, m)

    # ---------------------------------------------------------------------------
    #
    # ---------------------------------------------------------------------------
    def toLeftBasis(self, meshes_list):
        for m in meshes_list:
            command = [None, '1', '0', '0', '-90']
            self.Rotate(command, m)
            command = [None, '0', '0', '1']
            self.Mirror(command, m)

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def checkCmd(self, cmd, patern):
        return cmd.upper().lower() == patern.upper().lower()

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def loadTexture(self, command, mesh):
        mesh.texture_file = command[1]

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def setColor(self, command, mesh):
        for i in range(1, len(command)):
            try:
                mesh.diffuse_color.append(int(command[i]))
            except:
                mesh.diffuse_color.append(255)

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def setTextureCoordinates(self, command, mesh):
        try:
            v_idx = int(command[1])
            tx = float(command[2])
            ty = float(command[3])

            mesh.texcoords_list.append([v_idx, tx, ty])
        except:
            return

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def transformUV(self, meshes_list):

        for m in meshes_list:
            for tc in m.texcoords_list:
                if tc[2] > m.ty_max:
                    m.ty_max = tc[2]

            for i, tc in enumerate(m.texcoords_list):
                tc[2] = m.ty_max - tc[2]
                m.texcoords_list[i] = tc

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def loadCSV(self, filePath, is_transform = False):

        meshes_list = []

        # Open CSV file
        try:
            f = open(filePath, 'rt')
        except Exception as ex:
            print(ex)
            return meshes_list

        # Create temporary mesh

        # Read all file
        csv_text = f.read().split('\n')
        f.close()

        # Find first mesh
        idx = 0
        mesh_begin_idx = []

        for idx, line in enumerate(csv_text):
            command = self.parseLine(line)
            if self.checkCmd(command[0], "CreateMeshBuilder"):
               mesh_begin_idx.append(idx)


        for idx in range(0, len(mesh_begin_idx)):

            mesh = CSVmesh()

            a = mesh_begin_idx[idx]

            if idx + 1 >= len(mesh_begin_idx):
                b = len(csv_text)
            else:
                b = mesh_begin_idx[idx+1]

            for j in range(a, b):

                command = self.parseLine(csv_text[j])

                if self.checkCmd(command[0], "AddVertex"):
                    try:
                        x = float(command[1])
                        y = float(command[2])
                        z = float(command[3])
                        vertex = (x, y, z)
                        mesh.vertex_list.append(vertex)
                    except ValueError:
                        pass

                if self.checkCmd(command[0], "AddFace"):
                    self.addFace(command, mesh)

                if self.checkCmd(command[0], "AddFace2"):
                    self.addFace(command, mesh, True)

                # Create cube
                if self.checkCmd(command[0], "Cube"):
                    self.createCube(command, mesh)

                # Create cylinder
                if self.checkCmd(command[0], "Cylinder"):
                    self.createCylinder(command, mesh)

                # Translate mesh
                if self.checkCmd(command[0], "Translate"):
                    self.Translate(command, mesh)

                # Rotate mesh
                if self.checkCmd(command[0], "Rotate"):
                    self.Rotate(command, mesh)

                # Translate current mesh and all previos meshes
                if self.checkCmd(command[0], "TranslateAll"):
                    self.TranslateAll(command, meshes_list, mesh)

                # Rotate cureent mesh and all previos meshes
                if self.checkCmd(command[0], "RotateAll"):
                    self.RotateAll(command, meshes_list, mesh)

                # Scale meshes
                if self.checkCmd(command[0], "Scale"):
                    self.Scale(command, mesh)

                if self.checkCmd(command[0], "ScaleAll"):
                    self.ScaleAll(command, meshes_list, mesh)

                # Mirror meshes
                if self.checkCmd(command[0], "Mirror"):
                    self.Mirror(command, mesh)

                if self.checkCmd(command[0], "MirrorAll"):
                    self.MirrorAll(command, meshes_list, mesh)

                # Shear meshes
                if self.checkCmd(command[0], "Shear"):
                    self.Shear(command, mesh)

                if self.checkCmd(command[0], "ShearAll"):
                    self.ShearAll(command, meshes_list, mesh)

                # Load textures
                if self.checkCmd(command[0], "LoadTexture"):
                    self.loadTexture(command, mesh)

                # Set diffuse color
                if self.checkCmd(command[0], "SetColor"):
                    self.setColor(command, mesh)

                # Set texture coordinates
                if self.checkCmd(command[0], "SetTextureCoordinates"):
                    self.setTextureCoordinates(command, mesh)

            meshes_list.append(mesh)

        for m in meshes_list:
            print("v:" + str(len(m.vertex_list)) + "," +
                  "f:" + str(len(m.faces_list)))

        # Convertion to Blender basis
        #if is_transform:
         #   self.toRightBasis(meshes_list)

        # Transform texture coordinates to blender format
        self.transformUV(meshes_list)

        return meshes_list

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def generateModel(self, csv_text, meshes_list):

        for mesh in meshes_list:
            # New mesh
            csv_text.append("\n; " + mesh.name + "\n")
            csv_text.append("CreateMeshBuilder,\n")

            # Vertices
            for v, n in zip(mesh.vertex_list, mesh.normals_list):
                addVertex = "AddVertex, "

                for coord in v:
                    addVertex = addVertex + str(coord) + ", "

                for coord in n:
                    addVertex = addVertex + str(coord) + ", "

                csv_text.append(addVertex + "\n")


            csv_text.append("\n")

            # Faces
            for face in mesh.faces_list:

                if mesh.is_addFace2:
                    addFace = "AddFace2, "
                else:
                    addFace = "AddFace, "

                for v_idx in face:
                    addFace = addFace + str(v_idx) + ", "
                csv_text.append(addFace + "\n")

            csv_text.append("\n")

            # Diffuse color
            setColor = "SetColor, "
            for c in mesh.diffuse_color:
                setColor = setColor + str(c) + ","
            csv_text.append(setColor + "\n")

            # Decale color
            if mesh.is_decale:
                setDecalTransparentColor = "SetDecalTransparentColor, "
                for c in mesh.decale_color:
                    setDecalTransparentColor = setDecalTransparentColor + str(c) + ","
                csv_text.append(setDecalTransparentColor + "\n")

            # Texture
            if mesh.texture_file != "":
                loadTexture = "LoadTexture, " + mesh.texture_file
                csv_text.append(loadTexture + "\n")

                for t_idx, tc in enumerate(mesh.texcoords_list):
                    setTextureCoordinates = "SetTextureCoordinates, "
                    setTextureCoordinates = setTextureCoordinates + str(t_idx) + "," + str(round(tc[1], 3)) + "," + str(round(tc[2], 3)) + ","
                    csv_text.append(setTextureCoordinates + "\n")

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def export(self, path, meshes_list, left_coords_transform = True):

        if len(meshes_list) == 0:
            print("Please, select objects for export")
            return

        csv_text = []
        csv_text.append(";------------------------------------------------------\n")
        csv_text.append("; CSV exporter from Blender, RGUPS, Dmitry Pritykin\n")
        csv_text.append(";------------------------------------------------------\n")

        # Conversion to left basis
        #if left_coords_transform:
         #   self.toLeftBasis(meshes_list)

        # Transform UV coordinates
        self.transformUV(meshes_list)
        # Generate mesh
        self.generateModel(csv_text, meshes_list)

        try:

            # Output in file
            f = open(path, "wt", encoding="utf-8")
            f.writelines(csv_text)
            f.close()

        except Exception as ex:
            print(ex)
            return

