from hematovision_ml.classes import CLASS_NAMES, class_index, class_name


def test_canonical_class_order_has_nine_classes():
    assert CLASS_NAMES == (
        "Basófilos", "Eosinófilos", "Eritroblastos", "Linfoblastos", "Linfocitos",
        "Mieloblastos", "Monocitos", "Neutrófilos", "Plaquetas",
    )
    assert len(CLASS_NAMES) == 9
    assert class_index("Neutrófilos") == 7
    assert class_name(8) == "Plaquetas"
