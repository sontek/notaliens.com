"""
 _   _ _____ ____  _____   ____  _____ 
| | | | ____|  _ \| ____| | __ )| ____|
| |_| |  _| | |_) |  _|   |  _ \|  _|  
|  _  | |___|  _ <| |___  | |_) | |___ 
|_| |_|_____|_| \_\_____| |____/|_____|
 ____  ____      _    ____  ___  _   _ ____  
|  _ \|  _ \    / \  / ___|/ _ \| \ | / ___| 
| | | | |_) |  / _ \| |  _| | | |  \| \___ \ 
| |_| |  _ <  / ___ \ |_| | |_| | |\  |___) |
|____/|_| \_\/_/   \_\____|\___/|_| \_|____/ 

            ______________
      ,===:'.,            `-._
           `:.`---.__         `-._
             `:.     `--.         `.
               \.        `.         `.
       (,,(,    \.         `.   ____,-`.,
    (,'     `/   \.   ,--.___`.'
,  ,'  ,--.  `,   \.;'         `
 `{D, {    \  :    \;
   V,,'    /  /    //
   j;;    /  ,' ,-//.    ,---.      ,
   \;'   /  ,' /  _  \  /  _  \   ,'/
         \   `'  / \  `'  / \  `.' /
          `.___,'   `.__,'   `.__,' 

We import from * for all the models to have a nice place for SQLAlchemy
to pull all the models it needs.  Without them it wouldn't know which ones
to create on initialize of the database
"""

from notaliens.core.models   import *
from notaliens.people.models import *
from notaliens.sites.models  import *

# Be careful, I'm about to do *SCIENCE*!
# We export only models on import * that way we don't
# clog the namespace with things the models are using
__all__ = [
    k for k, v in locals().items()

    if (
        isinstance(v, type) and issubclass(v, Base)
    )
]
