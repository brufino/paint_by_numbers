from PIL import Image, ImageFilter, ImageDraw, ImageFont
import random

import numpy as np
import matplotlib.pyplot as plt


def draw(file_name, P, N, M=3):
    img = Image.open('images/'+file_name, 'r')
    pixels = img.load()
    size_x, size_y = img.size

    def dist(c1, c2):
        return (c1[0]-c2[0])**2+(c1[1]-c2[1])**2+(c1[2]-c2[2])**2

    def mean(colours):
        n = len(colours)
        r = sum(c[0] for c in colours)//n
        g = sum(c[1] for c in colours)//n
        b = sum(c[2] for c in colours)//n
        return (r,g,b)

    def colourize(colour, palette):
        return min(palette, key=lambda c: dist(c, colour))

    def cluster(colours, k, max_n=10000, max_i=10):
        colours = random.sample(colours, max_n)
        centroids = random.sample(colours, k)
        i = 0
        old_centroids = None
        while not(i>max_i or centroids==old_centroids):
            old_centroids = centroids
            i += 1
            labels = [colourize(c, centroids) for c in colours]
            centroids = [mean([c for c,l in zip(colours, labels)
                               if l is cen]) for cen in centroids]
        return centroids

    def label_map(palette):
        unique_cluster = list(set(palette))
        labels = {unique_cluster[i]:i for i in range(len(unique_cluster))}
        return labels

    def image_by_label(coords, pixels, labels, width, height):
        label_image = [[-1 for x in range(width)] for y in range(height)]
        for x,y in coords:
            label_image[x][y] = labels.get(pixels[x,y],-1000)
        return label_image

    all_coords = [(x,y) for x in range(size_x) for y in range(size_y)]
    all_colours = [pixels[x,y] for x,y in all_coords]
    palette = cluster(all_colours, P)
    labels = label_map(palette)
    print('clustered')

    # colorize each pixel to nearest cluster
    for x,y in all_coords:
        pixels[x,y] = colourize(pixels[x,y], palette)
    print('colourized')

    median_filter = ImageFilter.MedianFilter(size=M)
    img = img.filter(median_filter)
    pixels = img.load()
    for x,y in all_coords:
        pixels[x,y] = colourize(pixels[x,y], palette)
    print('median filtered')

    def neighbours(edge, outer, colour=None):
        return set((x+a,y+b) for x,y in edge
                   for a,b in ((1,0), (-1,0), (0,1), (0,-1))
                   if (x+a,y+b) in outer
                   and (colour==None or pixels[(x+a,y+b)]==colour))

    def cell(centre, rest):
        colour = pixels[centre]
        edge = set([centre])
        region = set()
        while edge:
            region |= edge
            rest = rest-edge
            edge = set(n for n in neighbours(edge, rest, colour))
        return region, rest

    print('start segmentation:')
    rest = set(all_coords)
    cells = []
    while rest:
        centre = random.sample(rest, 1)[0]
        region, rest = cell(centre, rest-set(centre))
        cells += [region]
        print('%d pixels remaining'%len(rest))
    cells = sorted(cells, key=len, reverse=True)
    print('segmented (%d segments)'%len(cells))

    print('start merging:')
    while len(cells)>N:
        small_cell = cells.pop()
        n = neighbours(small_cell, set(all_coords)-small_cell)
        for big_cell in cells:
            if big_cell & n:
                big_cell |= small_cell
                break
        print('%d segments remaining'%len(cells))
    print('merged')

    for cell in cells:
        colour = colourize(mean([pixels[x,y] for x,y in cell]), palette)
        for x,y in cell:
            pixels[x,y] = colour

    def visit_all_pixels(coords, label_image, size_x, size_y):
        outline_image = [[0 for x in range(size_x)] for y in range(size_y)]
        text_locations = []
        visited = [[0 for x in range(size_x)] for y in range(size_y)]
        fill_image = [[0 for x in range(size_x)] for y in range(size_y)]
        for x in range(size_x):
            for y in range(size_y):
                if(visited[x][y]==0):
                    print("working on pixel X: %d Y: %d out of %d , %d" %(x,y,size_x,size_y))
                    fill_image,visited = outline(label_image, fill_image, x, y, size_x, size_y, visited)
                    outline_image = border(fill_image, outline_image, size_x, size_y)
                    fill_image_no_border = np.subtract(np.array(fill_image),np.array(outline_image))
                    fill_image_no_border = fill_image_no_border.tolist()
                    text_locations.append(get_text_location(fill_image_no_border, x, y, label_image,size_x,size_y))
                    fill_image = [[0 for x in range(size_x)] for y in range(size_y)]
        return outline_image, text_locations
    
        
    def outline(label_image, fill_image, px, py, size_x, size_y, visited):
        fill_stack = []
        fill_stack.append([px,py])
        cur_val = label_image[px][py]
        
        while len(fill_stack) > 0:
            row, col = fill_stack.pop()
            if((row>=0) and (row<size_x) and (col>=0) and (col<size_y) and not(visited[row][col]) and (label_image[row][col]==cur_val)):
                fill_image[row][col] = 255
                visited[row][col] = 255
                fill_stack.append([row+1,col])
                fill_stack.append([row-1,col])
                fill_stack.append([row,col+1])
                fill_stack.append([row,col-1])    
        return fill_image, visited

    def border(fill_image, outlines, size_x, size_y):
        nxo = [0,1,0,-1]
        nyo = [1,0,-1,0]
        for x in range(size_x):
            for y in range(size_y):
                for n in range(4):
                    new_x = x+nxo[n]
                    new_y = y+nyo[n]
                    if((new_x>=0) and (new_x<size_x) and (new_y>=0) and (new_y<size_y)):
                        if((fill_image[new_x][new_y] != fill_image[x][y]) and (outlines[new_x][new_y] != 1)):
                            outlines[x][y] = 1
        return outlines

    def get_text_location(fill_image,x,y,label_image,size_x,size_y):
        val = label_image[x][y]
        count = 0
        for row in range (size_x):
            for col in range(size_y):
                if(fill_image[row][col]==255):
                    count+=1
        
        flag = random.randint(0,count-1)
        count_ones = 0
        for row in range(size_x):
            for col in range(size_y):
                if(fill_image[row][col]==255):
                    count_ones+=1
                    if(flag==count_ones):
                        return(row, col, val)

    def neighborsSame(mat, x, y):
        width = len(mat[0])
        height = len(mat)
        val = mat[y][x]
        xRel = [1, 0]
        yRel = [0, 1]
        for i in range(0,len(xRel)):
            xx = x + xRel[i]
            yy = y + yRel[i]
            if xx >= 0 and xx < width and yy >= 0 and yy < height:
                if mat[yy][xx]!=val :
                    return False
        return True

    def outlines(mat):
        width = len(mat[0])
        height = len(mat)
        # line = [[0]*width]*height
        # for y in range(0,height):
        #     for x in range(0,width):
        #         line[y][x] = 0 if neighborsSame(mat, x, y) else 1

        lineFlat = [0 if neighborsSame(mat, x, y) else 1 for y in range(0,height) for x in range(0,width)]
        line = [lineFlat[i:i+height] for i in range(0, len(lineFlat), height)]

        return line

    label_image = image_by_label(all_coords, pixels, labels, size_x, size_y)
    border_image,text_image = visit_all_pixels(all_coords, label_image, size_x, size_y)

    np_border = np.asarray(border_image)
    np_border = np.transpose(np_border)

    np_border = np_border^1
    im_border = Image.fromarray(np.uint8(np_border)*255,'L')
  
    print('colorized again')

    im_border= im_border.convert('RGB')
    draw = ImageDraw.Draw(im_border)
    fnt = ImageFont.truetype("arial.ttf",8)

    for i in range(len(text_image)):
        x, y, text = text_image[i]
        draw.text((x,y), str(text), font=fnt, fill=(0,0,0))

    img = img.convert('RGB')
    
    im_border.save('images/''P%d N%d OUTLINE' %(P,N)+file_name)
    img.save('images/''P%d N%d '%(P,N)+file_name)
    print('saved')

draw('dancing.jpg', 6, 50)