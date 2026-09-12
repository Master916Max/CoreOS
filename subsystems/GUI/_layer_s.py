from pygame import Surface

class Layer:
    def __init__(self, idx, surface:Surface):
        self.idx = idx
        self.surface = surface
        self.visible = True

    def get(self) -> Surface:
        return self.surface

class LayerManager:
    def __init__(self, base_surface:Surface):
        self.base_surface = base_surface
        self.layers = []

    def add_layer(self, layer: Layer):
        self.layers.append(layer)
        self.layers.sort(key=lambda x: x.idx)  # Sort layers based on their index

    def remove_layer(self, layer: Layer):
        self.layers.remove(layer)

    def get_layers(self):
        return [layer.get() for layer in self.layers if layer.visible]

    def render(self):
        for layer in self.layers:
            if layer.visible:
                self.base_surface.blit(layer.get(), (0, 0))  # Blit each visible layer onto the base surface
    