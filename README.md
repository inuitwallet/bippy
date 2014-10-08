#Bippy 
###fast and easy BIP0038 encryption and vanity addresses for NuBits and NuShares

Bippy is a port of Bippy [https://github.com/inuitwallet/bippy] specifically for NuBits and NuShares [https://nubits.com/]

Bippy is able to generate valid NuBit and NuShare private keys and addresses. It uses a customised BIP0038 encryption method [https://github.com/bitcoin/bips/blob/master/bip-0038.mediawiki] to add passphrase protected encryption to the private keys. Using a customised version of vanitygen [https://github.com/inuitwallet/vanitygen], Bippy is able to generate vanity addresses for NuBits or NuShares and offer optional BIP0038 style encryption on those private keys too.

###Installing Bippy

Bippy is built using Python 2.7 [https://www.python.org/downloads/] and Kivy [http://kivy.org/#download]. 
Both will need to be installed on your computer before Bippy will run. There are good instructions for installing both Python and Kivy on their respective websites. 

On Windows Kivy comes as a portable application. It can be a bit of a faff to get it working first time but the instructions on the Kivy site are clearer than I can manage here.
I intend to build some binary versions of Bippy in the near future which should make this step unneccessary. I will update this README when that happens.

###Runing Bippy

Once you have Python and Kivy installed simply clone this repository and run the Bippy.py file
The command used differs on different OSes. On Linux you use 'python Bippy.py'. On Mac you use 'kivy Bippy.py'. On windows you have to go through the procedure laid out on the Kivy website. 
Again, once I have compiled some executable versions, this will be unneccessary.

Bippy can be used totally offline. It also has no cache (unlike a web browser) so the keys it generates can be considered 'cold'.

###Using Bippy

Bippy is intended to be simple and to have an obvious workflow. There are instructions given on every action so it should be fairly self explanitory. 
You can choose what action you want to undertake byt selecting from the 'Action' drop down menu on the top bar.
When generating a vanity address, you need to choose either NuBits or NuShares as your currency (default is NuBits). this is done from the second dropdown on the top bar which is only active on the Vanity Address screen. 
To generate a vanity address, just enter the text you want to search for. Don't enter the standard prefix for Nubits ('B') or NuShares ('S') as Bippy adds these automatically.

If at any point you want to stop the Action and return to the home screen, press the main Bippy logo on the far left of the top bar. This will reset all the screens and remove any data that has been entered or generated

###The science bit

####BIP0038

The BIP0038 encryption method had to be modified slightly to work with NuBits and NuShares. Each valid private key can be used to hash an address for both NuBits and NuShares. The first step of the BIP0038 method is to generate an 'addresshash' which is added to the encrypted private key output. This is used to verify that the correct private key has been obtained when decryption happens. 
To avoid confusion as to which address to use I decided to concatenate both possible addresses together:

addresshash = sha256(sha256(NuBits_address + Nushares_Address))[:4]

Aside from that change, the BIP0038 method remians the same.

####Vanitygen

The vanitygen binary used by Bippy has been modified to always generate compressed private and public keys. this keeps it inline with the rest of the private nad public keys Bippy is able to create.
It has also been modified to accept two version numbers when a different version is specified. This allows for Nubit addresses to be generated which have a different version number to their corresponding private key.

####Entropy

When generating private keys internally, Bippy uses three different sources of Entropy. The most obvious is the user entered entropy which is collected when you draw dots over Bippy with your mouse. This is combined with clock based and urandom based entropy to generate random private keys for better security.


###Known Issues

The issues at the moment are to do with the compiling of the binaries that Bippy needs to run. The two it uses are scrypt (fopr BIp0038 encryption) and vanitygen 9for vanity address generation).
Bippy currently has scrypt binaries for:
Linux (64 bit)
Linux (32 bit)
OSX (64 bit)
Windows (32 bit)

and vanitygen binaries for:
Linux (64 bit)

If you are able to compile vanitygen or scrypt for platforms not mentioned, please do so and share the binary with me. Thanks :)
