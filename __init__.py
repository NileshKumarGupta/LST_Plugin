
def classFactory(iface):
    """
    This function is called when QGIS is loading plugins.
    Returns a "plugin object", as such.
    """
    from .mainLST import LSTplugin
    return LSTplugin(iface)
