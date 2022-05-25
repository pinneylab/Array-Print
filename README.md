<img src="images/array_print.png" alt="Array Print" align="right"/>

# Array Print
Array printing python notebook for use with a Scienion liquid-handling robot.

<code>Array Print</code> takes a <code>.csv</code> containing a MITOMI-assayable library in a 384-well layout and returns a Scienion-compatible <code>.fld</code> file and a <code>.csv</code> record of the array layout. Array Print optimizes the number of biological replicates that appear in the experiment and their placement within the print array to minimize cross-chamber contamination during MITOMI experiments. If prior information about the reactivity of library members exists, the user may bin members by acitivity level and Array Print prioritize placing less reactive members upstream on the array to minimize contamination along the flowpath.
