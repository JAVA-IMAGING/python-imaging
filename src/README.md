# DEVELOPER NOTES

So far, the image processing goes as follows:

1. Collect dark frames and generate a master dark frame

2. Collect flat frames and subtract it with master dark frame

3. Combine the resulting flat images together

4. Color convert the flat images based on their Bayer pattern and separate the resulting color into their own channels 

5. Subtract master dark frame from object/target image

6. Debayer the object image and separate them into their own color channels (like step 4)

7. Apply flat frame correction for each channel of the image

8. Align the corrected images and combine (not sure how yet) <~~~ _(We are here)_

Extra info that might be helpful:

- Make sure the Bayer pattern of flats and darks are the same with the image it is trying to process. Astronomical images can have differing Bayer patterns, but we cannot process them with flats and darks of a different pattern

- Try to match the dark frame params (exposure time, temperature, etc.) with the images you are going to perform the dark correction to.

- Figure out image alignment