import pandas as pd
import os

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "csv")

def _csv(name, **kwargs):
    return pd.read_csv(os.path.join(DATA, name), encoding="utf-8-sig", **kwargs)

def load_all():
    clientes  = _csv("clientes.csv",  parse_dates=["fecha_registro"])
    pedidos   = _csv("pedidos.csv",   parse_dates=["fecha_pedido"])
    detalles  = _csv("detalle_pedidos.csv")
    productos = _csv("productos.csv")
    tipos     = _csv("tipos_cliente.csv")
    etapas    = _csv("etapas_trazabilidad.csv")
    canales   = _csv("canales.csv")

    clientes = clientes.merge(tipos,  on="id_tipo_cliente",                              how="left")
    clientes = clientes.merge(etapas, left_on="id_etapa_trazabilidad", right_on="id_etapa", how="left")
    pedidos  = pedidos.merge(canales, on="id_canal",                                    how="left")

    return clientes, pedidos, detalles, productos, tipos, etapas, canales
