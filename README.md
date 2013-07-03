# Instamojo API Client, Python implementation.

## Installation 

Requirements:

 * **docopt**
 * **requests**

If you're using virtualenv, then

    $ pip install -r requirements.txt

If not, you might want to add a sudo:

    $ sudo pip install -r requirements.txt


## Usage:

    $ python instamojo.py [options]

**Note:** Since this is an example application, we're keeping things simple and not making this into a full-fledged application. Which means your authentication file 'auth.json' will be placed in your working directory. This is useful to keep the script compatible for *nix and Windows developers.

### Authenticate:

    $ python instamojo.py auth <username>

This will prompt you for entering password, and then use the credentials to get auth token from Instamojo API and store it in auth.json file for later use.

You can discard/delete the token by issuing:

    $ python instamojo.py auth delete

### Creating an Offer:

    $ python instamojo.py offer create \
      --title="My First Comic" \
      --description="Adventures of a digital nomad." \
      --file=digital_nomad.zip
      --inr=50

This will create an offer that will be priced for ₹50. You 
can share the URL for the offer wherever you wish.

### Listing All Your Offers:

    $ python instamojo.py offer

### Listing a specific Offer:

    $ python instamojo.py offer <slug>

Instamojo recognizes offers by their unique slugs (string that identifies the Offer in urls), you can pass slugs of any of the offers you have created to get more information.


