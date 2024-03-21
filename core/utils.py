def get_object_or_none(model_name, **kwargs):
    try:
        obj = model_name.objects.get(**kwargs)
        return obj
    except model_name.DoesNotExist:
        return None


def _cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id
