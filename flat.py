import datetime
import math
'''
https://marlinfw.org/docs/gcode
- Start at bottom left corner
- xDelta / yDelta = Total area for each pass
- zDelta = How far you want to come down
- zStepSize = Depth per pass
- speed = Spindle Speed
- feed = mm/min for levelling operation
- cutterWidth = Diameter of the cutter
'''

def flat(xDelta, yDelta, zDelta, zStepSize, speed, feed, cutterWidth):
    le = "\n"
    b=  ""
    b += "(" + datetime.datetime.now().strftime("%Y/%B/%d/ at %H:%M:%S:%p") +")" + le
    b += "(xDelta = " + v(xDelta) + ")" + le
    b += "(yDelta = " + v(yDelta) + ")" + le
    b += "(zDelta = " + v(zDelta) + ")" + le
    b += "(zStepSize = " + v(zStepSize) + ")" + le
    b += "(speed = " + v(speed) + ")" + le
    b += "(feed = " + v(feed) + ")" + le    

    # Note: zDelta + zStepSize are passed in as postive numbers
    # But: They need they need to be negative numbers to be aligned with the coord system
    zDelta = zDelta * -1.0
    zStepSize = zStepSize * -1.0

    x = 0.0
    y = 0.0
    z = 0.0
        
    b += le + "(Starting Spindle)" + le
    b += "M3 S" + v(speed) + le
    
    b += "(Do nothing and allow the spindle up to speed)" + le
    b += "M0 S3" + le
  
    b += "(Set the master feed rate)" + le
    b += "G01 F" + v(feed) + le
    
    b += "(Lower the head to Z0 before we begin - half the feed rate)" + le
    b += "G01 Z" + v(z) + " " + "F" + v(feed / 4) + le

    # Main loopy bit
    zp = 1    
    while zp == 1:
        # Move the cutting head down by the delta amount
        z += zStepSize
        
        # ensure we don't remove to much of the z goes past the zDelta
        if z < zDelta:
            z = zDelta
            zp = 0

        b += le + "(Starting a new x/y pass!)" + le
        b += "(Lower the head to to target z for this x/y pass - 1/4 rate)" + le
        b += "(Target Z = " + v(z) + ")" + le
        b += "G01 Z" + v(z) + " " + "F" + v(feed / 4) + le
        
        lastPass = False
        yp = 1
        while yp == 1:            
            # Flip x to the other end
            if x == 0:
                x = xDelta
            else:
                 x = 0

            # move the head along the x
            b += "G01 X" + v(x) + " Y" + v(y) + " Z" + v(z) + le            

            if lastPass:
                break 

            # Move y up, but never over shoot
            # Assuming a 40% overlap
            overlap = (1.0 - 0.4) * cutterWidth
            y += overlap
            if y > yDelta:
                y = yDelta
                lastPass = True

            b += "G01 X" + v(x) + " Y" + v(y) + " Z" + v(z) + le            
        # End while yp
        # Need to return to 0,0,2
        x = 0.0
        y = 0.0        

        b += "(Returning head for next pass)" + le
        b += "G01 X" + v(x) + " Y" + v(y) + " Z" + v(2) + le            
    # End while zp

    # Y boarder on each side?
    
    # Wrap it up
    b += le + "(Stopping Spindle)" + le
    b += "M05" + le

    b += le + "(End - All done!)" + le
    
    # Write the file
    f = open("flat.nc", "w")
    f.write(b)
    f.close()

def v(value: float):    
    b = str(value)
    b = "{:.2f}".format(value)
    return b
   