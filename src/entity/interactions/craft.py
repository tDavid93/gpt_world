def create_task(recipe, ingredients, tool, place):
    if recipe.tool == tool and recipe.ingredients == ingredients and recipe.place == place:
        return True, recipe
    else:
        return False, None