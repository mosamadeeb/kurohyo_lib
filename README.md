# kurohyo_lib
Library for reading Kurohyo 1 and 2 file formats. Made in python 3.8.

Supports reading ELPK containers, as well as the following formats:
- **base**: Skeleton base transforms
- **came**: Camera settings
- **imag**: Image references (for materials)
- **ligh**: Light objects
- **mate**: Materials (for models)
- **MIG**: GIM Textures (partial support only)
- **mode**: Models
- **pose**: Animations (for skeletons and cameras)
- **skel**: Skeleton hierarchy

# Installing
This was created for use with Blender addons, so you need to install [mathutils](https://pypi.org/project/mathutils/).

# Credits
[CapitanRetraso](https://github.com/CapitanRetraso) for [rELPKckr](https://github.com/CapitanRetraso/rELPKckr), which was adapted into [elpk.py](./kurohyo_lib/structure/elpk.py)
