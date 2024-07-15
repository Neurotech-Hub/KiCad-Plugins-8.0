import pcbnew
import FootprintWizardBase
import math
import PadArray as PA

class SpiralAntenna(FootprintWizardBase.FootprintWizard):
    def GetName(self):
        return "Spiral Antenna"

    def GetDescription(self):
        return "Generates a circular spiral antenna footprint based on specified parameters"

    def GetValue(self):
        return "Antenna_{outer}x{inner}mm".format(
            outer=self.parameters["Antenna"]["radius_outer"],
            inner=self.parameters["Antenna"]["radius_inner"]
        )

    def GenerateParameterList(self):
        self.AddParam("Antenna", "radius_outer", self.uMM, 50.0, min_value=1.0, max_value=500.0)
        self.AddParam("Antenna", "radius_inner", self.uMM, 35.0, min_value=1.0, max_value=500.0)
        self.AddParam("Antenna", "turns", self.uInteger, 5, min_value=1, max_value=500)
        self.AddParam("Antenna", "segments_per_turn", self.uInteger, 36, min_value=3, max_value=10000)
        self.AddParam("Antenna", "trace_nm", self.uInteger, 600000, min_value=1, max_value=1000000)
        self.AddParam("Antenna", "silk_margin", self.uMM, 1.0, min_value=0.0, max_value=10.0)
        self.AddParam("Antenna", "name", self.uString, "spiral")
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
        radius_outer = self.parameters["Antenna"]["radius_outer"]
        radius_inner = self.parameters["Antenna"]["radius_inner"]
        turns = self.parameters["Antenna"]["turns"]
        segments = self.parameters["Antenna"]["segments_per_turn"]
        trace_nm = self.parameters["Antenna"]["trace_nm"]
        silk_margin = self.parameters["Antenna"]["silk_margin"]
        name = self.parameters["Antenna"]["name"]

        module = self.module
        module.SetReference("REF**")
        module.SetValue(name)

        if silk_margin >= 0:
            # Show outline on top silk
            circle = pcbnew.PCB_SHAPE(module)
            circle.SetShape(pcbnew.SHAPE_T_CIRCLE)
            circle.SetLayer(pcbnew.F_SilkS)
            circle.SetStart(self.draw.TransformPoint(0, 0))
            circle.SetEnd(self.draw.TransformPoint(0, radius_outer + silk_margin))
            circle.SetWidth(pcbnew.FromMM(0.15))
            module.Add(circle)

        # Create and add the first pad at the inner radius
        pad1 = self.GetPad()
        pad1.SetPosition(self.draw.TransformPoint(radius_inner, 0))
        pad1.SetPadName("1")
        module.Add(pad1)

        total_segments = turns * segments
        delta_radius = (radius_outer - radius_inner) / total_segments
        delta_angle = 2 * math.pi / segments

        radius = radius_outer
        angle = 0
        # width_in_nm = int(pcbnew.FromMM(trace_nm) * 1e6)  # Convert width to nanometers
        
        for i in range(total_segments):
            startX = radius * math.cos(angle)
            startY = radius * math.sin(angle)
            radius -= delta_radius
            angle += delta_angle
            endX = radius * math.cos(angle)
            endY = radius * math.sin(angle)

            line = pcbnew.PCB_SHAPE(module)
            line.SetShape(pcbnew.SHAPE_T_SEGMENT)
            line.SetLayer(pcbnew.F_Cu)
            line.SetStart(self.draw.TransformPoint(startX, startY))
            line.SetEnd(self.draw.TransformPoint(endX, endY))
            line.SetWidth(trace_nm)
            module.Add(line)

        # Create and add the second pad at the outer radius
        pad2 = self.GetPad()
        pad2.SetPosition(self.draw.TransformPoint(radius_outer, 0))
        pad2.SetPadName("2")
        module.Add(pad2)

SpiralAntenna().register()
