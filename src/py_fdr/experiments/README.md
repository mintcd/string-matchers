# Experimenting Asymptotic Behavior

I want to check if the match time does not increase linearly with the number of patterns.

For the simplest form, all patterns are of length 8

I generate 50k patterns of length 8 uniformly. All characters are supposed to be printable, so I cannot use str type but byte type. I have to implement a new version.

For this version, I will generate uniformly from a to z.