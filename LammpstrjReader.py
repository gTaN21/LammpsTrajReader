import numpy as np
from tqdm import tqdm

class LammpstrjReader:
    """ Reads the default Lammps dump format (.lammpstrj)
    It reads n_atoms, steps, xyz corrdinates wrapped
    or unwrapped.
    """
    def __init__(self, file):
        self.file = file     # Instance Variable

    def atoms(self):
        """ Gives number of atoms
        """
        with open(self.file,"r") as f:
            f.readline()  #ITEM: TIMESTEP
            f.readline()  #timestep
            f.readline()  # ITEM: NUMBER OF ATOMS
            n_atoms = int(f.readline())   # num atoms

        return n_atoms

    def steps(self):
        """ Gives number of frames and array of steps
        """
        timestep = []
        with open(self.file,"r") as f:
            for line in f:
                if line.startswith("ITEM: TIMESTEP"):
                    timestep.append(int(f.readline()))
        timestep = np.array(timestep)
        n_frames = np.shape(timestep)[0]

        return  n_frames,timestep

    def boxinfo(self, dim ='3d'):
        """ Extract lengths of the simulation box
        """
        with open(self.file,"r") as f:
            f.readline()  # ITEM: TIMESTEP
            f.readline()  # timestep
            f.readline()  # ITEM: NUMBER OF ATOMS
            f.readline()  # num atoms
            orthogonal = len(f.readline().split()) == 6 # ITEM BOX BOUNDS
            if orthogonal :
                 if dim == '2d':
                    xlo, xhi = map(float, f.readline().split()[:2])
                    ylo, yhi = map(float, f.readline().split()[:2])
                    xlen = xhi - xlo
                    ylen = yhi - ylo

                    return xlen, ylen

                 else:
                    xlo, xhi = map(float, f.readline().split())
                    ylo, yhi = map(float, f.readline().split())
                    zlo, zhi = map(float, f.readline().split())
                    xlen = xhi - xlo
                    ylen = yhi - ylo
                    zlen = zhi - zlo

                    return xlen, ylen, zlen

    def positions(self, dim='3d'):
        """ Extract positions xu yu zu / x y z
        """

        n_atoms = self.atoms()
        n_frames, _ = self.steps()

        data = []

        # Determine the number of columns based on the dimension
        if dim == '2d':
            column = 4  # id type xu yu
        else:
            column = 5  # id type xu yu zu
            #column = 8 # id type xu yu zu z y z

        with open(self.file,'r') as f:
            #for line in f:
            for line in tqdm(f, desc="Processing", total=n_frames*n_atoms):
                line_chunks = line.split()
                if line_chunks !="ITEM" and len(line_chunks) == column:
                    data.append(line_chunks)

        data = np.array(data)
        data = np.delete(data,[0,1],axis=1)
        data = data.astype(float)
        xyzu = data.reshape([n_frames,n_atoms,(column-2)])

        # -- for column == 8 xu,yu,zu,x,y,z --
        #data = data.reshape([n_frames,n_atoms,(column-2)])
        #xyzu = np.delete(data, [3,4,5],axis=2)
        #xyz = np.delete(data, [0,1,2],axis=2)
        #return xyzu, xyz
        return xyzu