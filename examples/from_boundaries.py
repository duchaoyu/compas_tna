from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import sqrt

import compas
import compas_tna

from compas.geometry import mesh_smooth_area
from compas.topology import trimesh_remesh

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_tna.equilibrium import horizontal
from compas_tna.equilibrium import horizontal_nodal
from compas_tna.equilibrium import vertical_from_zmax
from compas_tna.equilibrium import vertical_from_formforce

from compas_tna.viewers import FormViewer


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


vertices = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (10.0, 10.0, 0.0), (0.0, 10.0, 0.0)]
faces = [[0, 1, 2, 3]]

form = FormDiagram.from_vertices_and_faces(vertices, faces)

key = form.insert_vertex(0)

viewer = FormViewer(form, figsize=(10, 7))

viewer.draw_edges(width=0.5)

def callback(mesh, k, args):
    print(k)
    viewer.update_edges()
    viewer.update()

trimesh_remesh(
    form,
    1.0,
    kmax=200,
    allow_boundary_split=True,
    allow_boundary_swap=True,
    allow_boundary_collapse=False,
    callback=callback)

mesh_smooth_area(form, fixed=form.vertices_on_boundary())

viewer.update_edges()
viewer.update(pause=0.1)
viewer.show()

# ==============================================================================
# update the boundary conditions

boundaries = form.vertices_on_boundaries()

exterior = boundaries[0]
interior = boundaries[1:]

form.set_vertices_attribute('is_anchor', True, keys=exterior)

form.update_exterior(exterior, feet=1)
form.update_interior(interior)

# ==============================================================================
# create the force diagram

force = ForceDiagram.from_formdiagram(form)

# ==============================================================================
# compute equilibrium

force.attributes['scale'] = 1.0

x = form.get_vertices_attribute('x')
y = form.get_vertices_attribute('y')

xmin, xmax = min(x), max(x)
ymin, ymax = min(y), max(y)

d = sqrt((xmax - xmin) ** 2 + (ymax - ymin) ** 2)

horizontal_nodal(form, force)
vertical_from_formforce(form, force, density=1.0 / d)

print('scale:', force.attributes['scale'])
print('zmax:', max(form.get_vertices_attribute('z')))
print('residual:', form.residual())

# ==============================================================================
# visualise result

viewer = FormViewer(form, figsize=(10, 7))

viewer.draw_vertices(
    keys=list(form.vertices_where({'is_external': False})),
    text={key: "{:.1f}".format(attr['z']) for key, attr in form.vertices(True)}
)
viewer.draw_edges(
    keys=list(form.edges_where({'is_edge': True, 'is_external': False})),
    width=0.1,
)
viewer.draw_reactions(scale=1.0)
viewer.draw_forces(scale=1.0)

viewer.show()
