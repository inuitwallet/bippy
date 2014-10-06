#bippy 
###fast and easy BIP0038 encryption for multiple crypto-currencies
#####http://bippy.org

Keeping private keys is inherently unsafe. 
If a third party has access to your private key, they have access to all of your coins. 
BIP0038 encryption adds a layer of security to your private key by protecting it with a passphrase. 
A BIP0038 encrypted private key is useless without the passphrase, but with the passphrase it still gives you control of your coins.

bippy is a tool for quickly and securely generating BIP0038 encrypted keys for a range of crypto-currencies.

   - bippy can generate new private keys or encrypt existing keys.
   - bippy has a simple user interface with helpful instructions to make the encryption process easier.
   - After encrypting a key, bippy can show you copy and paste-able personalised links to woodwallets.io so that you can keep your BIP0038 encrypted key safe in style.
   - bippy does not need an internet connection so private key generation and encryption can be kept secure.
   - bippy aims to be cross-platform on modern operating system, open source, and free.
   
#Running bippy

Ensure that you have kivy installed (or bootstrapped if you are using the portable version on windows. That's all explained at http://kivy.org)
Open a command prompt / terminal in the bippy directory and type *python bippy.py* 

 
#Libraries used

   - kivy (http://kivy.org)
   - scrypt (https://pypi.python.org/pypi/scrypt/0.6.1)
   - deepcelerons' script was the foundation of inuit which in turn led to bippy (https://bitcointalk.org/index.php?topic=361092.0) 

#Sponsors

http://woodwallets.io


#Contributors: 

This software represent the joint efforts of Nico (hi@adva.io) [http://woodwallets.io] and Sam (contact@inuit-wallet.co.uk) [http://inuit-wallet.co.uk]
