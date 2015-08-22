g# -*- coding: UTF-8 -*-

from abc import ABCMeta, abstractmethod

class Soundex: 
    __metaclass__ = ABCMeta
    
    prefixLength = 1
    codeLength = 4
    
    def get(languageCode):
        return languages[languageCode]()
    get = staticmethod(get)
    
    def setLength(self, l):
        self.codeLength = l
        
    def setPrefixLength(self, l):
        self.prefixLength = l
    
    @abstractmethod
    def encode(self, string):
        pass
    
    def _mutate(code, spec):
        if len(spec) != 2:
            raise Exception("Soundex mutation spec must have exactly two elements")
        
        repl = spec[0]
        letters = spec[1]
        if len(repl) > 1:
            raise Exception("Replacement code in Soundex procedure must be exactly one letter long or empty")
        
        newstring = []
        for l in code:
            if l in letters:
                newstring.append(repl)
            else:
                newstring.append(l)
        return ''.join(newstring)
    _mutate = staticmethod(_mutate)
    
    def _collapseClusters(code):
        if len(code) < 2: return code
        keep = [code[0]]
        for i in range(1, len(code)):
            if code[i] != code[i-1]:
                keep.append(code[i])
        return ''.join(keep)
    _collapseClusters = staticmethod(_collapseClusters)
    
    def _forceLength(code, length):
        code = code[:length]
        code += '0' * (length - len(code))
        return code
    _forceLength = staticmethod(_forceLength)

class AmericanSoundex(Soundex):
    __characterClasses = {
              'Numeric':    ['X', '0123456789'],
              'Vocalic':    ['', 'aeiou'],
              'Open':       ['', 'hwy'],
              'Labial':     ['1', 'bfpv'],
              'Palatovelar':['2', 'cgjkqsxz'],
              'Alveolar':   ['3', 'dt'],
              'Lateral':    ['4', 'l'],
              'Nasal':      ['5', 'mn'],
              'Rhotic':     ['6', 'r']
    }
    
    def encode(self, string):
        code = string.lower()

        # Save the prefix and remove numbers
        prefix, code = code[:self.prefixLength], code[self.prefixLength:]
        code = self._mutate(code, self.__characterClasses['Numeric'])
        
        # Perform substitutions
        for cc in [ 'Open', 'Labial', 'Palatovelar', 'Alveolar', 'Lateral', 'Nasal', 'Rhotic']:
            code = self._mutate(code, self.__characterClasses[cc])

        code = self._collapseClusters(code)
        
        # Remove vowels
        code = self._mutate(code, self.__characterClasses['Vocalic'])

        return self._forceLength(prefix + code, self.codeLength)

class HaitianCreoleSoundex(Soundex):
    __characterClasses = {
              'Numeric':    ['X', '0123456789'],
              'Vocalic':    ['', u'aehiouáéíóúàèìòùâêîôû'],
              'Labial':     ['1', 'bfpv'],
              'Velar':      ['2', 'cgjkq'],
              'Palatal':    ['3', 'sxz'],
              'Alveolar':   ['4', 'dt'],
              'Lateral':    ['5', 'l'],
              'Nasal':      ['6', 'mn'],
              'Glide':      ['7', 'rwy']
    }
    
    def encode(self, string):
        code = string.lower()
        
        # Save the prefix
        prefix, code = code[:self.prefixLength], code[self.prefixLength:]
        code = self._mutate(code, self.__characterClasses['Numeric'])
        
        # Perform substitutions
        for cc in [ 'Labial', 'Velar', 'Palatal', 'Alveolar', 'Lateral', 'Nasal', 'Glide']:
            code = self._mutate(code, self.__characterClasses[cc])
            
        code = self._collapseClusters(code)
        
        # Remove vowels
        code = self._mutate(code, self.__characterClasses['Vocalic'])

        return self._forceLength(prefix + code, self.codeLength)

class SylhetiSoundex(Soundex):
    # Not all characters are represented; the remaining do not form classes with each other
    __characterClasses = {
              'FrontVowel':         ['1', 'eiy'],
              'BackVowel':          ['2', 'ouw'],
              'LowVowel':           ['3', 'a'],
              'LabialVoiced':       ['4', 'bv'],
              'LabialVoiceless':    ['5', 'pf'],
              'AlveolarVoiced':     ['6', 'jz'],
              'AlveolarVoiceless':  ['7', 'cs']
    }
    
    def encode(self, string):
        code = string.lower()
        
        # Save the prefix
        prefix, code = code[:self.prefixLength], code[self.prefixLength:]
        
        # Perform substitutions
        for cc in self.__characterClasses:
            code = self._mutate(code, self.__characterClasses[cc])
            
        code = self._collapseClusters(code)

        return self._forceLength(prefix + code, self.codeLength)

languages = {
         'eng':     AmericanSoundex,
         'eng-us':  AmericanSoundex,
         'kre':     HaitianCreoleSoundex,
         'syl':     SylhetiSoundex
         }
