import pcbnew
import FootprintWizardBase
import math
import PadArray as PA

class RectangularAntenna(FootprintWizardBase.FootprintWizard):
    def GetName(self):
        return "Rectangular Antenna"

    def GetDescription(self):
        return "Generates a rectangular spiral antenna footprint based on specified parameters"

    def GetValue(self):
        return "Antenna_{length}x{width}mm".format(
            length=self.parameters["Antenna"]["length"],
            width=self.parameters["Antenna"]["width"]
        )

    def GenerateParameterList(self):
        self.AddParam("Antenna", "length", self.uMM, 50.0, min_value=1.0, max_value=500.0)
        self.AddParam("Antenna", "width", self.uMM, 30.0, min_value=1.0, max_value=500.0)
        self.AddParam("Antenna", "turns", self.uInteger, 5, min_value=1, max_value=100)
        self.AddParam("Antenna", "trace_nm", self.uInteger, 600000, min_value=1, max_value=1000000)
        self.AddParam("Antenna", "trace_spacing", self.uMM, 1.0, min_value=0.1, max_value=50.0)
        self.AddParam("Antenna", "silk_margin", self.uMM, 1.0, min_value=0.0, max_value=10.0)
        self.AddParam("Antenna", "style", self.uInteger, 0, min_value=0, max_value=1)
        self.AddParam("Antenna", "name", self.uString, "rectangle")
        self.AddParam("Pads", "pad_diameter", self.uMM, 0.6, min_value=0.1, max_value=5.0)
        self.AddParam("Pads", "drill_size", self.uMM, 0.35, min_value=0.1, max_value=2.0)

    def CheckParameters(self):
        pass

    def GetPad(self):
        pad_diameter = self.parameters["Pads"]["pad_diameter"]
        drill = self.parameters["Pads"]["drill_size"]
        shape = pcbnew.PAD_SHAPE_CIRCLE

        return PA.PadMaker(self.module).THPad(
            pad_diameter, pad_diameter, drill, shape=shape)

    def BuildThisFootprint(self):
        length = self.parameters["Antenna"]["length"]
        width = self.parameters["Antenna"]["width"]
        turns = self.parameters["Antenna"]["turns"]
        trace_nm = self.parameters["Antenna"]["trace_nm"]
        trace_spacing = self.parameters["Antenna"]["trace_spacing"]
        silk_margin = self.parameters["Antenna"]["silk_margin"]
        style = self.parameters["Antenna"]["style"]
        name = self.parameters["Antenna"]["name"]

        module = self.module
        module.SetReference("REF**")
        module.SetValue(name)

        if silk_margin >= 0:
            # Show outline on top silk
            rect = pcbnew.PCB_SHAPE(module)
            rect.SetShape(pcbnew.SHAPE_T_RECT)
            rect.SetLayer(pcbnew.F_SilkS)
            rect.SetStart(self.draw.TransformPoint(-width / 2 - silk_margin, -length / 2 - silk_margin))
            rect.SetEnd(self.draw.TransformPoint(width / 2 + silk_margin, length / 2 + silk_margin))
            rect.SetWidth(pcbnew.FromMM(0.15))
            module.Add(rect)

        trace_width = trace_nm * 1e-6

        if style == 1:
            xg = ((math.sqrt(2) - 1) * turns + 1) * (trace_width + trace_spacing)
            dx1 = (math.sqrt(2) - 1) * (trace_width + trace_spacing)
            dx2 = (trace_width + trace_spacing) * math.sqrt(2)
            dy = (trace_width + trace_spacing)

            x0 = 0
            y0 = length / 2
            d = 0

            for seg in range(turns * 6 + 1):
                if seg % 6 == 0:  # line goes left from middle
                    if seg == turns * 6:  # last iteration
                        x1 = 0
                    else:
                        x1 = x0 - (xg/2) - (width / 2 - xg / 2 - trace_width / 2 - d) - int(seg / 6) * dx1
                    y1 = y0
                elif seg % 6 == 1:  # line goes up
                    x1 = x0
                    y1 = y0 - (length - trace_width - 2 * d)
                elif seg % 6 == 2:  # line goes right
                    x1 = x0 + (width - trace_width - 2 * d)
                    y1 = y0
                elif seg % 6 == 3:  # line goes down
                    x1 = x0
                    y1 = y0 + (length - trace_width - 2 * d)
                elif seg % 6 == 4:  # line goes left to the middle
                    x1 = x0 + (xg/2) - (width / 2 - xg / 2 - trace_width / 2 - d) - (turns - 1 - int(seg / 6)) * dx1
                    y1 = y0
                elif seg % 6 == 5:  # line from the middle with a slope to the next level
                    x1 = x0 - dx2 + dx1
                    y1 = y0 - dy
                    d += trace_spacing + trace_width

                # DRAW LINE HERE
                line = pcbnew.PCB_SHAPE(module)
                line.SetShape(pcbnew.SHAPE_T_SEGMENT)
                line.SetLayer(pcbnew.F_Cu)
                line.SetStart(self.draw.TransformPoint(x0, y0))
                line.SetEnd(self.draw.TransformPoint(x1, y1))
                line.SetWidth(trace_nm)
                module.Add(line)

                x0 = x1
                y0 = y1

            # Create and add the first pad at the inner starting point
            pad1 = self.GetPad()
            pad1.SetPosition(self.draw.TransformPoint(0, length / 2))
            pad1.SetPadName("1")
            module.Add(pad1)

            # Create and add the second pad at the outer ending point
            pad2 = self.GetPad()
            pad2.SetPosition(self.draw.TransformPoint(0, y0))
            pad2.SetPadName("2")
            module.Add(pad2)
        else:
            x0 = -width / 2
            y0 = length / 2
            dx = width - trace_width
            dy = length - trace_width

            # Create and add the first pad at the inner starting point
            pad1 = self.GetPad()
            pad1.SetPosition(self.draw.TransformPoint(x0, y0))
            pad1.SetPadName("1")
            module.Add(pad1)

            for seg in range(0, turns * 4):
                if seg % 4 == 0:  # line goes up
                    x1 = x0
                    y1 = y0 - dy
                elif seg % 4 == 1:  # line goes right
                    if int(seg / 4) > 0:  # not for 1st right
                        dx = dx - trace_width - trace_spacing
                    x1 = x0 + dx
                    y1 = y0
                elif seg % 4 == 2:  # line goes down
                    if int(seg / 4) > 0:  # not for 1st down
                        dy = dy - trace_width - trace_spacing
                    x1 = x0
                    y1 = y0 + dy
                elif seg % 4 == 3:  # line goes left
                    dx = dx - trace_width - trace_spacing
                    x1 = x0 - dx
                    y1 = y0
                    dy = dy - trace_width - trace_spacing

                # DRAW LINE HERE
                line = pcbnew.PCB_SHAPE(module)
                line.SetShape(pcbnew.SHAPE_T_SEGMENT)
                line.SetLayer(pcbnew.F_Cu)
                line.SetStart(self.draw.TransformPoint(x0, y0))
                line.SetEnd(self.draw.TransformPoint(x1, y1))
                line.SetWidth(trace_nm)
                module.Add(line)

                x0 = x1
                y0 = y1

            # Create and add the second pad at the outer ending point
            pad2 = self.GetPad()
            pad2.SetPosition(self.draw.TransformPoint(x0, y0))
            pad2.SetPadName("2")
            module.Add(pad2)



RectangularAntenna().register()
