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
        self.AddParam("Antenna", "name", self.uString, "rectangle")
        self.AddParam("Pads", "pad_diameter", self.uMM, 1.0, min_value=0.1, max_value=5.0)
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

        # Starting point for the antenna
        x = 0
        y = length / 2

        posX = width / 2
        negX = -width / 2
        posY = length / 2
        negY = -length / 2

        # Create and add the first pad at the inner starting point
        pad1 = self.GetPad()
        pad1.SetPosition(self.draw.TransformPoint(x, y))
        pad1.SetPadName("1")
        module.Add(pad1)

        for i in range(turns):
            # Horizontal right to left
            line = pcbnew.PCB_SHAPE(module)
            line.SetShape(pcbnew.SHAPE_T_SEGMENT)
            line.SetLayer(pcbnew.F_Cu)
            line.SetStart(self.draw.TransformPoint(x, y))
            x = negX
            line.SetEnd(self.draw.TransformPoint(x, y))
            line.SetWidth(trace_nm)
            module.Add(line)
            negX += trace_spacing

            # Vertical top to bottom
            line = pcbnew.PCB_SHAPE(module)
            line.SetShape(pcbnew.SHAPE_T_SEGMENT)
            line.SetLayer(pcbnew.F_Cu)
            line.SetStart(self.draw.TransformPoint(x, y))
            y = negY
            line.SetEnd(self.draw.TransformPoint(x, y))
            line.SetWidth(trace_nm)
            module.Add(line)
            negY += trace_spacing

            # Horizontal left to right
            line = pcbnew.PCB_SHAPE(module)
            line.SetShape(pcbnew.SHAPE_T_SEGMENT)
            line.SetLayer(pcbnew.F_Cu)
            line.SetStart(self.draw.TransformPoint(x, y))
            x = posX
            line.SetEnd(self.draw.TransformPoint(x, y))
            line.SetWidth(trace_nm)
            module.Add(line)
            posX -= trace_spacing

            # Vertical bottom to top
            line = pcbnew.PCB_SHAPE(module)
            line.SetShape(pcbnew.SHAPE_T_SEGMENT)
            line.SetLayer(pcbnew.F_Cu)
            line.SetStart(self.draw.TransformPoint(x, y))
            y = posY - trace_spacing
            line.SetEnd(self.draw.TransformPoint(x, y))
            line.SetWidth(trace_nm)
            module.Add(line)
            posY -= trace_spacing

        # Create the final line connecting to the second pad
        line = pcbnew.PCB_SHAPE(module)
        line.SetShape(pcbnew.SHAPE_T_SEGMENT)
        line.SetLayer(pcbnew.F_Cu)
        line.SetStart(self.draw.TransformPoint(x, y))
        line.SetEnd(self.draw.TransformPoint(0, y))
        line.SetWidth(trace_nm)
        module.Add(line)

        # Create and add the second pad at the outer ending point
        pad2 = self.GetPad()
        pad2.SetPosition(self.draw.TransformPoint(0, y))
        pad2.SetPadName("2")
        module.Add(pad2)

RectangularAntenna().register()
