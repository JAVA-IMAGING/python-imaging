# DEVELOPER NOTES

So far, the image processing goes as follows:

1. Collect dark frames and generate a master dark frame

2. Collect flat frames and subtract it with master dark frame

3. Combine the resulting flat images together

4. Color convert the flat images based on their Bayer pattern and separate the resulting color into their own channels <~~~ _(We are here)_

5. Subtract master dark frame from object/target image

6. Debayer the object image and separate them into their own color channels (like step 4)

7. Apply flat frame correction for each channel of the image

8. Align the corrected images and combine (not sure how yet)

Extra info that might be helpful:

- The actual dark frames we've been given comes with a Bayer pattern. So the subtraction can get more complicated since it will be done per color channel if it doesn't match the target image to be subtracted from.
