# HeisenMICR Font

This is an ASCII-art representation of the "HeisenMICR" True-Type Font,
which is a variation of the MICR font.  Each section below contains the
ASCII-art layout of each capital letter and number in this font.  Each
character is on a 7x7 grid layout, with `#` representing a solid part
of the character.  The font should be spaced as though it is in an 8x8 cell,
so that there is a spacing of one grid block between characters.

When converting this to TTF, render each grid block at a ratio of 1.8:1 height
to width.  Round all corners with a 1/8 grid block radius.  Grid blocks that
are touching diagonally must be joined diagnonally so that they are connected
with a line of 1 grid block thickness on the diagonal.

Do not allow any component of this font to overlap another component, and do
not leave any gaps between adjacent components.  Determine a single, continuous
line that surrounds each character, and also a continuous line for any interior
sections.

For each character, test that these assertions are true.

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
#####
#    #
#    #
#####
##   ##
##   ##
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
#######
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
#######
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
######
#     #
#
##   ##
##    #
##    #
######
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
##
##
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
   ##
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
   ##
   ##
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
