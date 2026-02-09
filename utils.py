def is_unique_constraint_error(e):
    return "UNIQUE constraint failed" in str(e)
def is_not_found(e):
    return "404" in str(e)