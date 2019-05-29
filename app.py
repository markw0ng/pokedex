from flask import Flask, render_template, request, redirect, url_for
import requests
import json
import os
import requests_cache
import time
app = Flask(__name__)
requests_cache.install_cache('pokeapi_cache', backend='sqlite', expire_after=18000)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/pokemon/")
def pokemon():
    return render_template('pokemon.html', found=None)

@app.route("/pokemon/<pokemon>")
def find_pokemon(pokemon):

    now = time.ctime(int(time.time()))
    #check pokemon exists from json file

    r = requests.get('https://pokeapi.co/api/v2/pokemon/%s/' % pokemon)
    print("Time: {0} / Used Cache: {1}".format(now, r.from_cache))
    # pokemon not found return not found template
    if(r.status_code == 404):
        print('#NOT FOUND')
        return render_template('pokemon.html',found=None,pokemon=pokemon)
    # write to cache for next time
    else:
        response = r.json()
        species = requests.get(response['species']['url'])
        print("Time: {0} / Used Cache: {1}".format(now, species.from_cache))
        response['species']['meta'] = species.json()

        for item in response['species']['meta']['flavor_text_entries']:
            if item['language']['name'] == 'en':
                response['species']['meta']['species_description'] = item['flavor_text']

        evochain = requests.get(response['species']['meta']['evolution_chain']['url'])
        response['species']['meta']['evolution_chain']['meta'] = evochain.json()


        if 'species' in response['species']['meta']['evolution_chain']['meta']['chain'].keys():
            print("found chain")
            response['species']['meta']['evolution_chain']['evolves_from_name'] = response['species']['meta']['evolution_chain']['meta']['chain']['species']['name']
        else:
            print("not found chain")


        return render_template('pokemon.html',pokemon = pokemon, pjson = json.dumps(response, indent=4, sort_keys=True), response = response, found=True)

# search pokemon
@app.route("/search", methods = ['POST','GET'])
def search():
    if request.method == 'POST':
        search_term = request.form['search']
        return redirect(url_for('find_pokemon',pokemon=search_term.lower().strip()))
    else:
        return render_template('search.html')

# search pokemon types
@app.route("/types/<type>")
def pokemon_types(type):
    now = time.ctime(int(time.time()))
    # check pokemon is in the list of known pokemon
    r = requests.get('https://pokeapi.co/api/v2/type/%s/' % type)
    print("Time: {0} / Used Cache: {1}".format(now, r.from_cache))
    # pokemon not found return not found template
    if(r.status_code == 404):
        print('#NOT FOUND')
        return render_template('types.html',found=True,type=type)
    # write to cache for next time
    else:
        response = r.json()
        return render_template('types.html',type = type, response = response, pjson = json.dumps(response, indent=4, sort_keys=True), found=True)

if __name__ == "__main__":
    app.run(debug=True)
