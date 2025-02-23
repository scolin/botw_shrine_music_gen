# -*- coding: utf-8 -*-
"""
This python program is a proposed implementation of the rules depicted in the following youtube video:
https://youtu.be/6logXysLpNk
where Nomax explains the rules behind the music in shrines in Zelda Breath of the Wild.
This program is accompanied with extremely poor attempts at recreating some individual sound files, based on what I could hear and whatever motivation I could muster at recreating them, so do not expect a beautiful or diverse music. They are here merely to support the proof-of-concept.
That being said, if the actual sound files can be extracted from the game in the format expected by this program, and after updating the expected file names in the program and the loop duration, I expect it should work.

Now for the rules and how I interpreted them.

Vertical:
- The bell instrument always plays, but in combination with another instrument layer
- If only two instrument layers are playing, it's always the bells and the arp
- The lead instrument layer only plays if all other instrument are also playing

Horizontal:
- Each variation of any layer (except the bell layer) can play maximum of one time in sequence
- Before the lead layer starts playing, the bell, arp, strings and bass layers play for one round
- The lead layer can play for a maximum of four times in sequence
- The same lead variation can play for a maximum of 2 times in sequence
- The same bell variation can play for a maximum of four times in sequence
- The arp instrument layer can play for a maximum of twenty times in sequence
- The arp and bell instrument layers can play together for a maximum of three times in sequence
- The arp layer is never absent for more than one round

The arp layer is replaced with a piano layer when a shrine is completed

Proposed interpretation:
Vertical:
V1 The bell instrument always plays, but in combination with another instrument layer
    When initializing the layers, initialize it with the bell layer at least
V2 If only two instrument layers are playing, it's always the bells and the arp
    When having chosen the layers that will be played, if there are only two layers and the arp is not part of it, set the 2 layers to bell+arp
V3 The lead instrument layer only plays if all other instrument are also playing
    Check the layers: if the lead is present but another instrument is missing, remove the lead

Horizontal:
H1 Each variation of any layer (except the bell layer) can play maximum of one time in sequence
    There is some leeway for interpretation, but based on the youtube video, a variation would be a given combination of numbered instruments. So if talking about sound files, the next set of sound files shall not be the exact same as the current set,	so it is possible to have some sound files in common but not everything, and the bell layer is excluded from this criterion.
H2 Before the lead layer starts playing, the bell, arp, strings and bass layers play for one round
    It is not entirely clear, it can be interpreted as:
	1) Each other layer shall have at least played once before the lead layer can be chosen as a layer. 
	2) There shall have been at least one loop when all other layers have been played together before the lead layer can be chosen as a layer.
	1) is the one where the lead layer would appear the fastest on average, 2) is for a more crescendo appearance of all instruments
H3 The lead layer can play for a maximum of four times in sequence
    If for the next loop the lead layer will play a fifth time in sequence, then remove it -- this also means that if there were 3 layers and removing the lead will lead to a bell +  not a arp, this needs to be retransformed into bell+arp.
	But, this cannot happen because the lead only plays when all other instruments are playing -- so there cannot have been 3 layers playing but the 5 -- we can remove the lead layer safely.
H4 The same lead variation can play for a maximum of 2 times in sequence
    If playing a lead sound file, and this was played already twice before, then retry for another lead sound file
	This only works if there are at least 2 possible lead sound files, of course
H5 The same bell variation can play for a maximum of four times in sequence
    Same as above, but for four times, and at least 2 bell sound files. So, retry for another bell sound file
H6 The arp instrument layer can play for a maximum of twenty times in sequence
    If the arp layer was played twenty times, remove this layer? But this can challenge the other layer rules.
H7 The arp and bell instrument layers can play together for a maximum of three times in sequence
    This one is harder to interpret. The youtube video shows clearly that there are more than two times when the arp and bell layers play together -- only they are accompanied by other instruments. So maybe this means that arp+bell solely can only play 4 times in sequence, after that there needs to be more instrument (to avoid a too quiet music for too long?).
H8 The arp layer is never absent for more than one round
    Easier: if the arp layer is not in the previous loop, add it to this one.

Given the mix of rules related to layers and individual sound files, I tried to propose a reordering of the rules that would not require to restart too much the random selection of layers and files.

@author: Samuel Colin
"""
import os
import random
import pygame
import time

class AudioMixer:
    def __init__(self, base_path):
        # Initialize pygame mixer
        pygame.mixer.init()

        # Define file categories and their details
        self.layers = {
            'Bell': ['Bell_{:02d}.wav'.format(i) for i in range(2)],
            'Arp': ['Arp_{:02d}.wav'.format(i) for i in range(2)],
            'Bass': ['Bass_{:02d}.wav'.format(i) for i in range(2)],
            'Strings': ['Strings_{:02d}.wav'.format(i) for i in range(2)],
            'Lead': ['Lead_{:02d}.wav'.format(i) for i in range(2)]
            }

        # Full paths to wav files
        self.file_paths = {
            cat: [os.path.join(base_path, file) for file in files] 
            for cat, files in self.layers.items()
        }
            
        self.previous_loop = {}
        self.current_loop = {}

        # Tracking variables
        self.non_played_non_lead_layers = set(self.layers.keys()) - {'Lead'}
        self.consecutive_bell_arp_only = 0
        
        # Tracking for consecutive plays
        self.plays = {
            'Bell': {'file': None, 'file_count': 0, 'layer_count': 0},
            'Arp': {'file': None, 'file_count': 0, 'layer_count': 0},
            'Bass': {'file': None, 'file_count': 0, 'layer_count': 0},
            'Lead': {'file': None, 'file_count': 0, 'layer_count': 0},
            'Strings': {'file': None, 'file_count': 0, 'layer_count': 0}
        }

    def new_loop(self):
        valid_loop = False
        next_plays = {}
        while not valid_loop:
            valid_loop = True
            # V1, first part of the sentence
            layers = set({'Bell'})
            # Randomly select other layers
            other_layers = list(set(self.layers.keys()) - {'Bell'})
            # At least one other layer will be selected: V1, second part of the sentence
            add_layers = random.randint(1, len(other_layers))
            layers.update(random.sample(other_layers, add_layers))
            print("V1: ", layers)
            
            # V3
            if 'Lead' in layers:
                non_lead_layers = set(self.layers.keys()) - {'Lead'}
                current_non_lead_layers = set(layers) - {'Lead'}
                if non_lead_layers != current_non_lead_layers:
                    layers.remove('Lead')
            print("V3: ", layers)
            
            # H2, interpretation 1
            if len(self.non_played_non_lead_layers) > 0:
                layers.discard('Lead')
            print("H2: ", layers)
            
            # H3
            if self.plays['Lead']['layer_count'] >= 4:
                layers.discard('Lead')
            print("H3: ", layers)
            
            # H6
            if self.plays['Arp']['layer_count'] >= 20:
                layers.discard('Arp')
            print("H6: ", layers)
            
            # H8
            if self.plays['Arp']['layer_count'] == 0:
                layers.add('Arp')
            print("H8: ", layers)
            
            # V2
            if len(layers) <= 2 and not ('Arp' in layers):
                layers = {'Bell', 'Arp'}
            print("V2: ", layers)

            current_files = set()
            for lay in self.plays:
                if lay != 'Bell':
                    current_files.add(self.plays[lay]['file'])
            
            # Now select the files to be played -- and see if they match the remaining horizontal rules
            new_selection = False
            while not new_selection:
                new_selection = True
                for lay in layers:
                    next_plays[lay] = random.choice(self.file_paths[lay])

                print("Proposed next plays:", next_plays)

                # H4
                if 'Lead' in next_plays:
                    if next_plays['Lead'] == self.plays['Lead']['file']:
                        if self.plays['Lead']['file_count'] >= 2:
                            next_plays['Lead'] = random.choice(self.file_paths[lay])
                print("H4: ", next_plays)
                
                # H5
                if 'Bell' in next_plays:
                    if next_plays['Bell'] == self.plays['Bell']['file']:
                        if self.plays['Bell']['file_count'] >= 4:
                            next_plays['Bell'] = random.choice(self.file_paths[lay])
                print("H5: ", next_plays)
                
                next_files = set()
                for lay in next_plays.keys():
                    if lay != 'Bell':
                        next_files.add(next_plays[lay])
                # H1
                if next_files == current_files:
                    new_selection = False
                    print("H1 failed, retrying a file selection")
                    
            # H7
            if self.consecutive_bell_arp_only >= 3:
                if layers == {'Bell', 'Arp'}:
                    valid_loop = False
                    print("H7 failed, retrying another layer selection")
        # At this point we passed all the rules
        return next_plays
            
            
    def play_loop(self, i, duration=10):
        """Play the selected files for a specified duration."""


        # Update play tracking
        self.previous_loop = self.current_loop
        self.current_loop = self.new_loop()
        print("Playing loop ", i, ": ",self.current_loop)
        
        # Housekeeping the various tracking
        for lay in self.layers:
            if lay not in self.current_loop:
                self.plays[lay] = {'file': None, 'file_count': 0, 'layer_count': 0}
            else:
                self.plays[lay]['layer_count'] = self.plays[lay]['layer_count'] + 1
                if self.current_loop[lay] == self.plays[lay]['file']:
                    self.plays[lay]['file_count'] = self.plays[lay]['file_count'] + 1
                else:
                    self.plays[lay]['file_count'] = 0
                    self.plays[lay]['file'] = self.current_loop[lay]

        if len(self.non_played_non_lead_layers) > 0:
            self.non_played_non_lead_layers = self.non_played_non_lead_layers - set(self.current_loop.keys())
        
        # Because of the V2 rule, we know that if there are only 2 layers, it shall be the Bell and the Arp
        if len(self.current_loop) == 2:
            self.consecutive_bell_arp_only = self.consecutive_bell_arp_only + 1
        else:
            self.consecutive_bell_arp_only = 0
                

        # Play files simultaneously
        channels = {}
        for lay, file_path in self.current_loop.items():
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(pygame.mixer.Sound(file_path))
                channels[lay] = channel
        
        # Sleep for loop duration
        time.sleep(duration)
        
        # Stop all channels
        for channel in channels.values():
            channel.stop()

    def run(self, num_loops=10, loop_duration=10):
        """Run the audio mixer for specified number of loops."""
        for i in range(num_loops):
            self.play_loop(i, duration=loop_duration)

# Example usage
if __name__ == "__main__":
    base_path = "sound"  # Replace with your actual path
    mixer = AudioMixer(base_path)
    mixer.run(num_loops=100)
