# from https://github.com/zordsdavini/abcex

class Abcex:

    abc_map = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 'a',
            11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f', 16: 'g', 17: 'h', 18:
            'i', 19: 'j', 20: 'k', 21: 'l', 22: 'm', 23: 'n', 24: 'o', 25: 'p',
            26: 'q', 27: 'r', 28: 's', 29: 't', 30: 'u', 31: 'v', 32: 'w', 33:
            'x', 34: 'y', 35: 'z'}

    inv_abc_map = {str(v): k for k, v in abc_map.items()}

    def encode(self, number):
        number = int(number)
        result = ''

        while number > 0:
            result = "%s%s" % (self.abc_map[number % 36], result)
            number //= 36

        return result


    def decode(self, string):
        result = 0
        string = str(string)
        string = reversed(str(string))

        for i, c in enumerate(string):
            result = 36**i * self.inv_abc_map[c] + result

        return result

