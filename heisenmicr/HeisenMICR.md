# HeisenMICR

HeisenMICR is a monospaced, MICR-style display typeface. It is inspired by the
**Moore Computer** typeface (1968) — itself an alphabetic extension of **E-13B**,
the magnetic-ink character-recognition (MICR) font that banks print along the
bottom edge of checks. Where E-13B defines only the ten digits and a few control
symbols, HeisenMICR carries the same blocky, machine-read look across the full
set of letters, digits, and ASCII punctuation.

This document is the complete and self-contained specification of the typeface:
the grids below define the shapes, and the sections that follow define the
metrics and the construction rules. Any implementation that follows them — in
any language or tool — will reproduce the font.

## The design grid

Every glyph is drawn on a **7×7 grid of square modules**. In each grid below,
`#` marks an inked module and a space marks an empty one; those two characters
are all that is needed. Rows read top to bottom, columns left to right. Only the
capitals A–Z, the digits 0–9, and the ASCII punctuation are drawn here — the
lowercase letters are derived from the capitals (see *Metrics*), and the space
character is an empty glyph.

## Metrics

All coordinates are given in font units on a **1000-unit em**.

- **Module.** An uppercase module is **55 units wide × 99 units tall**, a
  height-to-width ratio of **9∶5** (1.8). The extra height is what gives the
  face its tall, MICR-like proportions.
- **Cap height & baseline.** A capital fills all seven rows, so the **cap
  height** is 7 × 99 = **693 units**. Glyphs sit on the **baseline** at the
  bottom of the grid.
- **Advance width.** The face is **monospaced**. The 7-module body (7 × 55 =
  385 units) is inset by a one-module **side bearing** on each side, for an
  **advance width** of 9 × 55 = **495 units** — a full one-module gap on either
  side, so adjacent glyphs are separated by two modules.
- **Lowercase (small caps).** Lowercase letters reuse the capitals' grids,
  scaled vertically so the whole seven-row glyph stands at an **x-height** of
  **5/7 of the cap height** = **495 units**. Their module keeps the full 55-unit
  width, so a lowercase module is 55 × 70.71 units (ratio **9∶7**, ≈1.29). Like
  capitals, they rest on the baseline.

## Construction

Each glyph outline is built from its grid as follows.

1. **Modules.** Every inked module becomes a filled rectangle (55 units wide by
   the module height).
2. **Diagonal joins.** Two inked modules that touch only at a corner (a diagonal
   step) are bridged by a parallelogram *band* laid across that shared corner,
   with long edges at the module's own slope (height ÷ width: 9∶5 for capitals,
   9∶7 for small caps). A run of such steps therefore reads as one straight
   diagonal stroke instead of a staircase. A band is added in three cases:
   - **Free diagonal:** the two modules orthogonally between the pair are both
     empty (an isolated diagonal, as in the arms of `X` or the slash of `Z`).
   - **Into a stem:** exactly one of those two modules is filled (a stem), and
     the step continues an existing free-diagonal run — so the diagonal meets
     the stem cleanly instead of stepping into it (as in `M`, `N`, `W`, `1`).
   - **Corner bevel:** exactly one is filled, the empty one lies on the outer
     edge of the grid, and the stroke reverses there rather than branching
     onward — so an outer corner is cut to a single diagonal (the lower-right of
     `B`, the upper-left of `Q`, the lower-left of `U`, the curves of `S`).
3. **Union.** All rectangles and bands are merged into outline contours, with
   overlaps removed, so nothing double-covers and no seam is left between
   touching pieces.
4. **Rounding.** Every corner of the resulting outline — inner and outer — is
   rounded with a **circular arc whose radius is one quarter of the module
   width** (≈13.75 units). Where an edge is too short to fit two full arcs, the
   radius is reduced to fit.

## Invariants

A correctly built glyph satisfies all of the following, which also serve as
tests:

- **No overlaps, no gaps.** Re-merging the finished outline changes nothing, and
  modules that are edge- or diagonally-adjacent stay connected as one shape.
- **One line per shape.** Each connected run of modules is bounded by exactly one
  continuous **outer contour**, and each fully enclosed empty region by exactly
  one **inner contour** (counter). Disconnected **islands** are allowed — for
  example, the two center modules of `0` float inside its counter.
- **Faithful to the grid.** Sampling the rendered glyph at each module's center
  inks exactly the modules the grid marks with `#`.

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
