# HeisenMICR

HeisenMICR is a monospaced, MICR-style display typeface. Every glyph is drawn on
a **7×7 module grid**; in the sections below, `#` marks an inked module and a
space marks an empty one — those two characters are all the grid needs. The
grids are the single source of truth: `build.py` compiles them into
`HeisenMICR.ttf` and `test.py` verifies each rendering against its grid.

## Metrics

The font is drawn on a **1000-unit em**. Each module of an uppercase glyph is
**55 units wide × 99 units tall** (a 1.8∶1 height-to-width ratio), so the **cap
height** is 7 modules = 693 units and the glyph rests on the **baseline** at the
bottom row of the grid. Every glyph is **monospaced** with an **advance width**
of 9 modules = 495 units: the 7-module body carries a one-module **side bearing**
on the left and right, leaving a two-module gap between adjacent glyphs.

**Lowercase** letters are **small caps** — the same 7×7 grids as the capitals,
but set on a **1∶1 module** (55×55 units) so they fill the bottom square of the
uppercase area, from the baseline up to a 385-unit **x-height**. They are
derived from the capitals, so only A–Z, the digits, and the ASCII punctuation
are drawn below; the space glyph is empty.

## Rendering

Each glyph outline is constructed from its grid:

1. Every inked module becomes a rectangle.
2. **Diagonal joins** — where inked modules meet only at a corner, a slanted
   band bridges them so a staircase renders as one straight diagonal stroke
   (its slope is the module ratio: 1.8 for capitals, 1 for the square small
   caps). The same join lets a diagonal **run into a stem** without
   stair-stepping, and **bevels a stepped corner** on a glyph's outer edge into
   a single diagonal.
3. The rectangles and bands are combined with a **boolean union** into
   non-overlapping contours.
4. Every corner is **rounded** with a fillet of radius 14 units (about a quarter
   of a module width).

This yields one continuous **outer contour** per connected run of modules and
one **inner contour** (counter) per enclosed empty region. A glyph may contain
disconnected **islands** — for example, the two center modules of `0` float
inside its counter.

## Assertions

`test.py` checks every glyph against its grid: re-unioning the outline is a
no-op (no overlaps), edge- and diagonally-adjacent modules stay connected (no
gaps), there is exactly one outer contour per solid component and one inner
contour per enclosed hole, and the rasterized glyph inks exactly the grid's
filled modules.

## A

```
  ### 
 #   #
 #   #
 #####
##   ##
##   ##
##   ##
```

## B

```
######
#     #
#     #
######
##    #
##    #
######
```

## C

```
 ######
#
#
##
##
##
 ######
```

## D

```
######
#     #
#     #
##    #
##    #
##    #
######
```

## E

```
#######
#
#
######
##
##
#######
```

## F

```
#######
##
##
######
#
#
#
```

## G

```
 #####
#     #
#
##  ###
##    #
##    #
 #####
```

## H

```
 #   #
 #   #
 #   #
#######
##   ##
##   ##
##   ##
```

## I

```
#######
   #
   #
   ##
   ##
   ##
#######
```

## J

```
     #
     #
     #
     ##
#    ##
#    ##
#######     
```

## K

```
#     #
#    #
#   #
####
##  #
##   #
##    #
```

## L

```
#
#
#
##
##
##
#######
```

## M

```
#     #
##   ##
# # # #
#  #  #
#     #
##   ##
##   ##
```

## N

```
#    ##
##   ##
# #   #
#  #  #
#   # #
##   ##
##    #
```

## O

```
 #####
#     #
#     #
#     #
#     #
#     #
 #####
```

## P

```
######
##    #
##    #
######
#
#
#
```

## Q

```
 #####
##    #
##    #
#     #
#   # #
#    ##
 ######
```

## R

```
######
#     #
#     #
######
##  #
##   #
##    #
```

## S

```
 ######
#
#
 #####
     ##
     ##
######
```

## T

```
#######
   #
   #
   #
   ##
   ##
   ## 
```

## U

```
#     #
#     #
#     #
##    #
##    #
##    #
 #####
```

## V

```
##    #
##    #
##    #
#     #
 #   #
  # #
   #
```

## W

```
##   ##
##   ##
#     #
#  #  #
# # # #
##   ##
#     #
```

## X

```
##   ##
 #   #
  # #
   #
  # #
 #   #
##   ##
```

## Y

```
#     #
 #   #
  # #
   #
   #
   ##
   ##
```

## Z

```
#######
##   #
    #
   #
  #
 #   ##
#######
```

## 0

```
 #####
#     #
#     #
#  #  #
#  #  #
#     #
 #####
```

## 1

```
   #
  ##
 # #
   #
   #
  ####
  ####
```

## 2

```
#######
      #
      #
#######
##
##
#######
```

## 3

```
#######
      #
      #
#######
     ##
     ##
#######
```

## 4

```
#
#    #
#    #
#######
     ##
     ##
     ##
```

## 5

```
#######
#
#
#######
     ##
     ##
#######
```

## 6

```
#######
#
#
#######
##    #
##    #
#######
```

## 7

```
#######
     #
    #
   #
   #
   ##
   ##
```

## 8

```
#######
#    ##
#    ##
#######
#     #
#     #
#######
```

## 9

```
#######
#     #
#     #
#######
     ##
     ##
#######
```

## !

```
   #
   #
   #
   #
   #

   #
```

## "

```
  # #
  # #
```

## #

```
  # #
 #####
  # #
 #####
  # #
```

## $

```
   #
 #####
 #
 #####
     #
 #####
   #
```

## %

```
##
##   #
    #
   #
  #
 #   ##
     ##
```

## &

```
 ##
#  #
#  #
 ##
#  #
#  ##
 ## #
```

## '

```
   #
   #
   #
```

## (

```
   #
  #
 #
 #
 #
  #
   #
```

## )

```
 #
  #
   #
   #
   #
  #
 #
```

## *

```
   #
 # # #
  ###
 # # #
   #
```

## +

```

   #
   #
 #####
   #
   #
```

## ,

```




  ##
  ##
  #
```

## -

```



 #####
```

## .

```





  ##
  ##
```

## /

```
      #
     #
    #
   #
  #
 #
#
```

## :

```

  ##
  ##

  ##
  ##
```

## ;

```

  ##
  ##

  ##
  ##
  #
```

## <

```
   #
  #
 #
#
 #
  #
   #
```

## =

```


 #####

 #####
```

## >

```
#
 #
  #
   #
  #
 #
#
```

## ?

```
 ###
#   #
    #
   #
   #

   #
```

## @

```
 ###
#   #
# ###
# # #
# ###
#
 ###
```

## [

```
 ###
 #
 #
 #
 #
 #
 ###
```

## \

```
#
 #
  #
   #
    #
     #
      #
```

## ]

```
 ###
   #
   #
   #
   #
   #
 ###
```

## ^

```
   #
  # #
 #   #
```

## _

```






#######
```

## `

```
 #
  #
```

## {

```
   ##
  #
  #
 #
  #
  #
   ##
```

## |

```
   #
   #
   #
   #
   #
   #
   #
```

## }

```
##
  #
  #
   #
  #
  #
##
```

## ~

```



 ###
   ###
```
