#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Four-point sensitivties
-----------------------

In this example, we illustrate how to visualize the sensitivties of four-point
configurations. You can easily loop over the plotting command to create
something like this: https://www.youtube.com/watch?v=lt1qV-2d5Ps
"""

import numpy as np
import matplotlib.pyplot as plt
import pygimli as pg
import pygimli.meshtools as mt
import pygimli.physics.ert as ert

###############################################################################
# We start by creating a ERT data container with 3 single four-point
# configurations.
scheme = pg.DataContainerERT()

nelecs = 10
pos = np.zeros((nelecs, 2))
pos[:,0] = np.linspace(5, 25, nelecs)
scheme.setSensorPositions(pos)

measurements = np.array((
    [0,3,6,9], # Dipole-Dipole
    [0,9,3,6], # Wenner
    [0,9,4,5] # Schlumberger
))

for i, elec in enumerate("abmn"):
    scheme[elec] = measurements[:,i]

###############################################################################
# Now we set up a 2D mesh.

world = mt.createWorld(start=[0, 0], end=[30, -10], worldMarker=True)
for pos in scheme.sensorPositions():
    world.createNode(pos)

mesh = mt.createMesh(world, area=.05, quality=33, marker=1)

###############################################################################
# As a last step we invoke the ERT manager and calculate the Jacobian for a
# homogeneous half-space.

mgr = ert.ERTManager()
data = mgr.simulate(mesh, res=1, scheme=scheme)
mgr.invert(mesh=mesh, data=data)
model = np.ones(mesh.cellCount())
mgr.fop.createJacobian(model)

###############################################################################
# Final visualization

def get_abmn(scheme, idx):
    """ Get coordinates of four-point cfg with id `idx` from DataContainerERT
    `scheme`."""
    coords = {}
    for elec in "abmn":
        elec_id = int(scheme(elec)[idx])
        elec_pos = scheme.sensorPosition(elec_id)
        coords[elec] = elec_pos.x(), elec_pos.y()
    return coords


def plot_abmn(ax, scheme, idx):
    """ Visualize four-point configuration on given axes. """
    coords = get_abmn(scheme, idx)
    for elec in coords:
        x, y = coords[elec]
        if elec in "ab":
            color = "red"
        else:
            color = "blue"
        ax.plot(x, y, marker=".", color=color, ms=10)
        ax.annotate(elec.upper(), xy=(x, y), size=12, ha="center", fontsize=10, bbox=dict(
            boxstyle="round", fc=(0.8, 0.8, 0.8), ec=color), xytext=(0, 20),
                    textcoords='offset points', arrowprops=dict(
                        arrowstyle="wedge, tail_width=.5", fc=color, ec=color,
                        patchA=None, alpha=0.75))
        ax.plot(coords["a"][0],)

labels = ["Dipole-Dipole", "Wenner", "Schlumberger"]
fig, ax = plt.subplots(scheme.size(), 1, sharex=True, figsize=(8,8))
for i, sens in enumerate(mgr.fop.jacobian()):
    # Label in lower-left corner
    ax[i].text(.01,.15, labels[i],
        horizontalalignment='left',
        verticalalignment='top',
        transform=ax[i].transAxes, fontsize=12, fontweight="bold")

    # Electrode annotations
    plot_abmn(ax[i], scheme, i)

    # Log-scaled and normalized sensitvity
    normsens = pg.utils.logDropTol(sens/mesh.cellSizes(), 8e-4)
    normsens /= np.max(normsens)
    pg.show(mesh, normsens, cmap="RdGy_r", ax=ax[i], label="Normalized\nsensitvity",
            orientation="vertical", cMin=-1, cMax=1, nLevs=3)
