# CryptoAlexa

**Alexa + Sql + Csv**



***flask_ask Dependency bug***
* downgrade pip to pip 9.0 
    - works in python 2.7
    - Flask_ask wont install -  will give ModuleNotFoundError : pip.req 
    - so need to downgradepython -m pip install pip==9.0.3
* Windows: 
    - Install - Microsoft visual c++ compiler for python 2.7 
* Linux: 
    - pyopenssl require cyptography version 2.2 to work
      * install or downgrade   pip install 'cryptography<2.2'

                    
