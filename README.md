# Paint by Numbers
Takes an image and generates a version that can be painted by number

## Running the code
Please open up paint_to_numbers.py. The very last line in this script has all the power you need. Feel free to add an image to the image folder but I would recommend converting the size to be square (i.e. 1000x1000 pixels). The other two parameters within the function call is the number of colors and the maximum number of regions. I advise choosing an image with 1000x1000 pixels and good contrast. In my work, 10 colors and 200 regions turned out really well. The more colors and the more regions you specify, the longer the algorithm takes. Enjoy!

## Algorithm details
Most of this algorithm was due to the great work by [Emil](https://codegolf.stackexchange.com/questions/42217/paint-by-numbershttps://codegolf.stackexchange.com/questions/42217/paint-by-numbers).

The algorithm Emil made works as follows:
1. Find a colour palette of P colours by k-means clustering and paint the image in this reduced palette.
2. Apply a slight median filter to get rid of some noise.
3. Make a list of all monochromatic cells and sort it by size.
4. Merge the smallest cells with their respective largest neighbour until there are only N cells left.

I have extended this algorithm to provide an image with regions and a text number inside the region. I have done this by:

5. getting the unique number (color) of each pixel within the picture
6. drawing the border around the regions with same number
7. drawing the number randomly within the region (this sometimes draws just outside the region and needs further improvement)

In the future I would like too:

8. Set a minimum region size (i.e. 2x2 pixels)
9. Draw the text within the regions perfectly (instead of the odd error)
10. Add an output image which maps the color to the number (like a legend)

## Original Image:
![Image of dancing](/images/dancing.jpg?raw=true)
## Image converted to their painting by number form (REGIONS FILLED)
![Painted by numbers](/images/P6N75dancing.jpg?raw=true)
## Image converted to their paint by number form (REGIONS EMPTY)
![Paint by numbers](/images/P6N75OUTLINEdancing.jpg?raw=true)
