from conllu import parse_incr, TokenList

def voicing(input_file, output_file):
    
    for sentence in parse_incr(input_file):
        new_sentence = TokenList() # TokenList used to form new modified sentence
        
        for token in sentence:
            # check if token's "misc" collumn contains voicing annotation
            # if so, append it as a feature in its "feats" collumn
            misc = token["misc"]
            if misc != None and "Voicing" in misc:
                if misc["Voicing"] == "Voiced":
                    token["feats"]["Voicing"] = "Voiced"
                elif misc["Voicing"] == "Unvoiced":
                    token["feats"]["Voicing"] = "Unvoiced"
            
            new_sentence.append(token)

        # copy over original metadata
        new_sentence.metadata = sentence.metadata
        
        # append new altered sentence to desired output file
        with open(output_file, "a") as file:
            file.write(new_sentence.serialize())
