def tackle(*args, **kwargs):
    caster = args[0]
    target = kwargs.get('target')
    caster.move_to(target)