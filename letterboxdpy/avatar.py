class Avatar:
    # Default upscale size
    upscale_size = (1000, 1000)
    # List of default sizes to check against
    default_sizes = [(80, 80), (220, 220)]

    def __init__(self, url):
        # Parsing the URL to determine if the avatar exists
        self.top_level = url.split('.')[0].split('//')[1]
        # Top levels: avatar:a, statics:s,secure
        self.avatar_exists = self.top_level == 'a'
        # Storing the URL without query parameters if the avatar exists
        self.url = url.split('?')[0] if self.avatar_exists else url
        # Initializing data dictionary with initial state
        self.data = {
            'exists': self.avatar_exists,
            'upscaled': False,
            'url': self.url
        }
        # Storing a copy of data for internal use
        self._upscaled_data = self.data

    @property
    def upscaled_data(self):
        # If avatar exists, iterate through default sizes to check for matches
        if self.avatar_exists:
            for default_size in self.default_sizes:
                pattern_default = '-0-'.join(map(str, default_size))
                # If a match is found, update the data with upscaled information
                if pattern_default in self.url:
                    pattern_upscale = '-0-'.join(map(str, self.upscale_size))
                    self._upscaled_data.update({
                        'upscaled': True,
                        'url': self.url.replace(pattern_default, pattern_upscale)
                    })
        # Return the upscaled data
        return self._upscaled_data

if __name__ == '__main__':
    print(Avatar('https://unknown.example.com/test.png').upscaled_data)
    print(Avatar('https://s.example.com/a/0-220-0-220.png').upscaled_data)
    print(Avatar('https://a.example.com/a/0-220-0-220.png').upscaled_data)
    print(Avatar('https://a.example.com/a/0-80-0-80.png').upscaled_data)