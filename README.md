# botw_shrine_music_gen
A Python program for generating Zelda BOTW shrine music based on the rules described by Nomax

# Description (taken from the program header)

This python program is a proposed implementation of the rules depicted in the following youtube video:

[https://youtu.be/6logXysLpNk](https://youtu.be/6logXysLpNk)

where Nomax explains the rules behind the music in shrines in Zelda Breath of the Wild.

This program is accompanied with extremely poor attempts at recreating some individual sound files, based on what I could hear and whatever motivation I could muster at recreating them, so do not expect a beautiful or diverse music. They are here merely to support the proof-of-concept.

That being said, if the actual sound files can be extracted from the game in the format expected by this program, and after updating the expected file names in the program and the loop duration, I expect it should work.

Now for the rules and how I interpreted them.

## Vertical:
- The bell instrument always plays, but in combination with another instrument layer
- If only two instrument layers are playing, it's always the bells and the arp
- The lead instrument layer only plays if all other instrument are also playing

## Horizontal:
- Each variation of any layer (except the bell layer) can play maximum of one time in sequence
- Before the lead layer starts playing, the bell, arp, strings and bass layers play for one round
- The lead layer can play for a maximum of four times in sequence
- The same lead variation can play for a maximum of 2 times in sequence
- The same bell variation can play for a maximum of four times in sequence
- The arp instrument layer can play for a maximum of twenty times in sequence
- The arp and bell instrument layers can play together for a maximum of three times in sequence
- The arp layer is never absent for more than one round

The arp layer is replaced with a piano layer when a shrine is completed

# Proposed interpretation:
## Vertical:
- **V1** The bell instrument always plays, but in combination with another instrument layer

  When initializing the layers, initialize it with the bell layer at least
- **V2** If only two instrument layers are playing, it's always the bells and the arp

  When having chosen the layers that will be played, if there are only two layers and the arp is not part of it, set the 2 layers to bell+arp
- **V3** The lead instrument layer only plays if all other instrument are also playing

  Check the layers: if the lead is present but another instrument is missing, remove the lead

## Horizontal:
- **H1** Each variation of any layer (except the bell layer) can play maximum of one time in sequence
  
  There is some leeway for interpretation, but based on the youtube video, a variation would be a given combination of numbered instruments. So if talking about sound files, the next set of sound files shall not be the exact same as the current set,	so it is possible to have some sound files in common but not everything, and the bell layer is excluded from this criterion.
- **H2** Before the lead layer starts playing, the bell, arp, strings and bass layers play for one round

  It is not entirely clear, it can be interpreted as:
	1. Each other layer shall have at least played once before the lead layer can be chosen as a layer. 
	2. There shall have been at least one loop when all other layers have been played together before the lead layer can be chosen as a layer.
	
  Item i is the one where the lead layer would appear the fastest on average, item ii is for a more crescendo appearance of all instruments. In the implementation, item i was chosen.
- **H3** The lead layer can play for a maximum of four times in sequence

  If for the next loop the lead layer will play a fifth time in sequence, then remove it -- this also means that if there were 3 layers and removing the lead will lead to a bell +  not a arp, this needs to be retransformed into bell+arp.

  But, this cannot happen because the lead only plays when all other instruments are playing -- so there cannot have been 3 layers playing but the 5 -- we can remove the lead layer safely.
- **H4** The same lead variation can play for a maximum of 2 times in sequence

  If playing a lead sound file, and this was played already twice before, then retry for another lead sound file

  This only works if there are at least 2 possible lead sound files, of course
- **H5** The same bell variation can play for a maximum of four times in sequence

  Same as above, but for four times, and at least 2 bell sound files. So, retry for another bell sound file
- **H6** The arp instrument layer can play for a maximum of twenty times in sequence

  If the arp layer was played twenty times, remove this layer? But this can challenge the other layer rules.
- **H7** The arp and bell instrument layers can play together for a maximum of three times in sequence

  This one is harder to interpret. The youtube video shows clearly that there are more than two times when the arp and bell layers play together -- only they are accompanied by other instruments. So maybe this means that arp+bell solely can only play 4 times in sequence, after that there needs to be more instrument (to avoid a too quiet music for too long?).
- **H8** The arp layer is never absent for more than one round
  Easier: if the arp layer is not in the previous loop, add it to this one.

Given the mix of rules related to layers and individual sound files, I tried to propose a reordering of the rules that would not require to restart too much the random selection of layers and files.

