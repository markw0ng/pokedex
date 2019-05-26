from flask import Flask, render_template, request, redirect, url_for
import requests
import json
import os
app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/pokemon/")
def pokemon():
    return render_template('pokemon.html', found=None)

@app.route("/pokemon/<pokemon>")
def find_pokemon(pokemon):

    #check pokemon exists from json file
    pokemonlist = 'static/pokemon/pokemon.json'
    with open(pokemonlist) as f:
        pokemonlist = json.loads(f.read())

    # check pokemon is in the list of known pokemon
    if pokemon in pokemonlist['pokemon']:
        # set id of the pokemon found
        pokeid = pokemonlist['pokemon'].index(pokemon);
    else:
        # return not found template with suggestions
        return render_template('pokemon.html',found=None,pokemon=pokemon)

    # setup cache file
    filename = 'static/cache/pokemon/%s.json' % pokemon.lower()
    exists = os.path.isfile(filename)

    # check if cache file exists
    if exists:
        with open(filename) as f:
            response = json.loads(f.read())
        print('#FOUND CACHE')
        return render_template('pokemon.html',pokemon = pokemon, response = response, pjson = json.dumps(response, indent=4, sort_keys=True), found=True)        
    # if no cache file found refetch
    else:
        r = requests.get('https://pokeapi.co/api/v2/pokemon/%s/' % pokemon)
        # pokemon not found return not found template
        if(r.status_code == 404):
            print('#NOT FOUND')
            return render_template('pokemon.html',found=None,pokemon=pokemon)
        # write to cache for next time
        else:
            f = open(filename, "w")
            f.write(r.text)
            f.close()
            print('#FOUND FROM API')
            response = r.json()
            return render_template('pokemon.html',pokemon = pokemon, response = response, found=True)

# search pokemon
@app.route("/search", methods = ['POST','GET'])
def search():
    if request.method == 'POST':
        search_term = request.form['search']
        return redirect(url_for('find_pokemon',pokemon=search_term.lower().strip()))
    else:
        return render_template('search.html')

# search pokemon
@app.route("/types/<type>")
def pokemon_types(type):
    filename = 'static/cache/types/%s.json' % type.lower()
    exists = os.path.isfile(filename)

    # check if cache file exists
    if exists:
        with open(filename) as f:
            response = json.loads(f.read())
        print('#FOUND CACHE')
        return render_template('types.html',type = type, response = response, pjson = json.dumps(response, indent=4, sort_keys=True), found=True)
    # if no cache file found refetch
    else:
          
        return render_template('types.html', type = type)

if __name__ == "__main__":
    app.run(debug=True)
