Idk what I'm doin here.

TODO: 
 - defuq is copyright, can i just copy the license and be done?!
 - write this README
 - document shit. idk how sphinx works -> normal comments for now
 - I did setup.py with a tutorial. is it ok?

CODESTRUCTURE:
    Qty > Unit > Dimension (concerning complexity)
    relations and expressions are defined from the more to the less complex class
    ergo: Unit * Qty = Qty.rmul(Unit), not the other way around
