# Grale

A tiny command line tool I wrote to create gradient background for my phone

## Installing

`uv pip install .`

## Examples
<img width="300" height="300" alt="output" src="https://github.com/user-attachments/assets/b0e204fe-0999-4900-9985-8314a7d12b39" />



### Create a gradient for an iphone 14 pro max
```grale -g #0E0021,.15,#140047,.4,#7B99D1,1.0 -p 14_pro_max```

### Create a gradient going horizontally instead of vertically 
```grale -g #0E0021,.15,#140047,.4,#7B99D1,1.0 -p 14_pro_max -r```

### Create a gradient without specifying points, only colors
```grale -g #0E0021,#7B99D1 -p 14_pro_max```

### Create a gradient with an arbitrary size
```grale -g #0E0021,#7B99D1 -d 100,100```

### Create a gradient at an arbitrary location
```grale -g #0E0021,#7B99D1 -d 100,100 -o ~/Desktop/my_wallpaper.png```
