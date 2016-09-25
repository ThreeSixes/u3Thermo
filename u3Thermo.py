#!/usr/bin/python

# By ThreeSixes (https://githb.com/ThreeSixes)

###############
### Imports ###
###############

try:
	import u3
except:
	print("This program requires both the u3 and exodriver libraries from LabJack as well as the LabJack U3 device and input amplifier.")
	print("https://github.com/labjack/exodriver")
	print("https://github.com/labjack/LabJackPython")
try:
	import sqlite3
	canLog = True
except:
	print("Sqlite3 required for logging support. Logging will be disabled.")
import time
import traceback
import datetime
import json

try:
	from thermocouples_reference import thermocouples
except:
	print("This program requires the thermocouples_reference library which can be installed from Pip.")

from pprint import pprint


###############
### Logger  ###
###############

class logger():
	def __init__(self):
		"""
		Sqlite3 logger class.
		"""
		
		# Create master objects.
		self.__sqlInst = None
		self.__curse = None
	
	def setup(self, filePath = None):
		"""
		Set up the Sqlite 3 database.
		"""
		try:
			# If we're mssing a file path create a path in place with a default name based on the UTC timestamp.
			if filePath == None:
				dts = datetime.datetime.utcnow()
				filePath = "./log-%s.sqlite3" %dts.strftime('%Y%m%d-%H%M%S')
			
			# Open up database in the first place
			self.__sqlInst = sqlite3.connect(filePath)
			self.__curse = self.__sqlInst.cursor()
			
			# String to create necessary tables.
			createSql = "CREATE TABLE readings(id REAL PRIMARY KEY, data BLOB);"
			
			# Build our table.
			self.__curse.execute(createSql)
			self.__sqlInst.commit()
		except:
			raise
		
	def log(self, sid, data):
		"""
		Add record to our database.
		"""
		
		try:
			# Add records to the database.
			insertStr = "INSERT INTO readings VALUES('%s', '%s')" %(sid, data)
			self.__curse.execute(insertStr)
			self.__sqlInst.commit()
		
		except:
			raise
		
		return
		
	def close(self):
		"""
		Cleanly shut down the database.
		"""
		
		try:
			self.__sqlInst.close()
		except:
			tb = traceback.format_exc()
			print("Exploded trying to close our sqlite DB:\n%s" %tb)
		
		return

############################
### LabJack U3 hareware  ###
############################

class u3Interface():
	def __init__(self):
		"""
		Lab Jack interface for thermocouple.
		"""
		
		# Default system parameters.
		self.__u3Channel = 0
		self.__vOffset = 0.4
		self.__gainSetting = 51
		self.__tempUnits = 'C'
		self.__tcType = 'K'
		self.__debug = False
		self.__logData = False
		
		# Counters
		self.__sid = 0 # Sample ID
		
		# Temperature conversion matrix.
		self.__converter = {
			'K': float,
			'C': self.__kToC,
			'F': self.__kToF
		}
		
		try:
			# Set up library for a type K thermocouple.
			self.__tc = None
		except:
			raise
		
		try:
			# Create LabJack U3 object and set debugging.
			self.__u3 = u3.U3()
		except:
			raise
	
	def __kToC(self, degreesK):
		"""
		Convert degrees Kelvin to Celsius.
		C = K - 273.15
		"""
		
		retVal = 0
		
		try:
			# Convert degrees K to C
			retVal = degreesK - 273.15
		except:
			raise
		
		if self.__debug == True:
			print("Convert %s K -> %s C" %(degreesK, retVal))
		
		return retVal

	def __kToF(self, degreesK):
		"""
		Convert degrees Kelvin to Fahrenheit.
		F = (K * (9.0/5.0)) - 459.67
		"""
		
		retVal = 0
		
		try:
			# Convert degrees K to F.
			retVal = (degreesK * (9.0 / 5.0)) - 459.67
		except:
			raise
		
		if self.__debug == True:
			print("Convert %s K -> %s F" %(degreesK, retVal))
		
		return retVal
	
	def setup(self):
		"""
		Initial setup and config.
		"""
		
		try:
			if self.__debug == True:
				print("Setting up and calibrating LJTick-InAmp on channel %s" %self.__u3Channel)
			
			# Set analog channel.
			self.__u3.configAnalog(self.__u3Channel)
			# Calibrate temperature sensor.
			self.__u3.getCalibrationData()
		except:
			raise
		
		try:
			if self.__debug == True:
				print("Set up type %s thermocouple." %self.__tcType)
			
			# Set up our thermocouple.
			self.__tc = thermocouples[self.__tcType]
		except:
			raise
		
		return
	
	def getSID(self):
		"""
		Returns the current sample ID
		"""
		
		return self.__sid

	def setDebug(self, debugOn):
		"""
		Turn debugging on or off given a boolean argument.
		"""
		retVal = False
		
		try:
			try:
				# Make sure we have the right type.
				debugOn = bool(debugOn)
				self.__debug = debugOn
				
				if self.__debug == True:
					print("Debug = %s" %self.__debug)
			except:
				raise ValueError("Debug setting must be True or False.")
		except:
			raise
		
		return retVal
	
	def setTCType(self, tcType):
		"""
		Set thermocoupe type supported by the thermoccouple library.
		"""
		
		retVal = False
		
		if self.__debug == True:
			print("Thermocouple type = %s" %tcType)
		
		# Get the types of thermocouples supported by the libraray.
		tcTypes = thermocouples.keys()
		
		try:
			# Make sure we have a string that's upper case before comparing.
			tcType = str(tcType).upper()
			
			# Make sure we have a valid unit.
			if tcType in tcTypes:
				# Set it.
				self.__tcType = tcType
			else:
				raise ValueError("Thermocouple type must be one of %s" %tcTypes)
		
		except:
			raise
		
		return retVal

	def setChannel(self, channel):
		"""
		Set channel the input amp is attached to.
		"""
		
		retVal = False
		
		if self.__debug == True:
			print("LJTick-InAmp channel = %s" %channel)
		
		try:
			try:
				channel = int(channel)
			except:
				raise ValueError("Channel must be an integer.")
			
			self.__u3Channel = channel
			retVal = True
		except:
			raise
		
		return retVal
	
	def getTUnit(self):
		"""
		Return which temperature units we're using.
		"""
		
		return self.__tempUnits

	def setTUnit(self, unit):
		"""
		Set system units.
		"""
		
		retVal = False
		
		if self.__debug == True:
			print("Temperature unit = %s" %unit)
		
		try:
			# Make sure we have a string that's upper case before comparing.
			unit = str(unit).upper()
			
			# Make sure we have a valid unit.
			if unit in ['C', 'K', 'F']:
				# Set it.
				self.__tempUnits = unit
			else:
				raise ValueError("Units must be 'C', 'K', or 'F'.")
		
		except:
			raise
		
		return retVal

	def setVOffset(self, voffset):
		"""
		Set thermocouple voltage offset.
		"""
		
		retVal = False
		
		if self.__debug == True:
			print("Thermocouple voltage offset = %s" %voffset)
		
		try:
			try:
				voffset = float(voffset)
			except:
				raise ValueError("Voltage offset must be a number.")
			
			self.__vOffset = voffset
			retVal = True
		except:
			raise
		
		return retVal	

	def setGain(self, gain):
		"""
		Set input amp gain.
		"""
		
		retVal = False
		
		if self.__debug == True:
			print("LJTick-InAmp gain = %s" %gain)
		
		try:
			try:
				gain = int(gain)
			except:
				raise ValueError("Gain must be an integer.")
			self.__gainSetting = gain
			retVal = True
		except:
			raise
		
		return retVal	

	def cleanup(self):
		"""
		Clean up after use.
		"""
		
		if self.__debug == True:
			print("LabJack U3 cleanup called...")
		
		try:
			# Close the device and free it up.
			self.__u3.close()
		except:
			tb = traceback.format_exc()
			print("Exception closing LabJack U3:\n%s")
		
		return
	
	def getLJTemp(self):
		"""
		Get LabJack temperature sensor readings in degrees Kelvin.
		"""
		
		# Set return value.
		retVal = 0
		
		if self.__debug == True:
			print("Getting LabJack internal temp sensor reading...")
		
		try:
			# Get internal system temperature form LabJack in Kelvin
			retVal = self.__u3.getTemperature()
		except:
			raise
		
		return retVal
	
	def getCJTemp(self, degreesK, unitComp = False):
		"""
		Get cold junction temperature.
		"""
		retVal = degreesK
		
		try:
			if unitComp == True:
				# Do the temperature conversion.
				retVal = self.__converter[self.__tempUnits](retVal)
		except:
			raise
		
		return retVal

	def getTcVolts(self):
		"""
		Get thermocouple voltage.
		"""
		retVal = 0
		
		if self.__debug == True:
			print("Getting thermocouple voltage reading...")
		
		try:
			# Get readings.
			retVal = ((self.__u3.getAIN(self.__u3Channel) - float(self.__vOffset)) / float(self.__gainSetting)) * 1000.0
		except:
			raise
		
		return retVal
	
	def getTCReading(self, voltage, coldTemp, unitComp = False):
		"""
		Get temperature reading from thermocouple.
		"""
		
		# Increment sample ID.
		self.__sid += 1
		
		if self.__debug == True:
			print("Deriving unit-adjusted temperature from readings...")
		
		retVal = 0
		
		# Do the conversion.
		retVal = self.__tc.inverse_KmV(voltage, Tref=coldTemp)
		
		if unitComp == True:
			# Do the temperature conversion.
			retVal = self.__converter[self.__tempUnits](retVal)
		
		return retVal
	
	def buildJsonString(self, dts, coldTemp, voltage, tcTemp, tempUnit):
		"""
		Create a JSON string for logging.
		"""
		
		retVal = {}
		
		# Build the object and then dump as JSON string.
		retVal.update({'dts': str(dts), 'coldJctTemp': coldTemp, 'tcTemp': tcTemp, 'tcVolts': voltage, 'tempUnit': tempUnit})
		retVal = json.dumps(retVal)
		
		return retVal
	
	def log(self, entry):
		"""
		Log entry to database.
		"""
		
		# If we have SQLite 3 support....
		if canLog == True:
			None
		
		return

# If we're started from CLI...
if __name__ == "__main__":
	try:
		import argparse
		
		# Set up command line interface.
		parser = argparse.ArgumentParser(description = "Thermocouple monitor", epilog = "Requires a LabJack U3 device with a thermocouple attached to a LJTick-Inamp. This software has only been tested against a LabJack U3-LV using its internal temperature sensor as a cold junction thermometer.")
		parser.add_argument('--cold', action='store_true', help = 'Display cold junction temperature.')
		parser.add_argument('--unit', choices=['c', 'C', 'f', 'F', 'k', 'K'], help = 'Display temperatures in this unit. Defaults to Celsius (C).')
		parser.add_argument('--volts', action='store_true', help = 'Show thermocouple voltage?')
		parser.add_argument('--voffset', type=float, help = 'Specify thermocouple offset voltage. Should be around 0.4 or 1.25, defaults to 0.4.')
		parser.add_argument('--gain', type=int, help = 'Gain configured on the LabJack LJTick-InAmp. Defaults to 51.')
		parser.add_argument('--channel', type=int, help = 'Channel number with LabJack LJTick-InAmp attached to it. Defaults to 0.')
		parser.add_argument('--tctype', choices=thermocouples.keys(), help = 'Type of thermocouple attached to LabJack LJTick-InAmp. Defaults to type K.')
		parser.add_argument('--log', action='store_true', help = 'Activate data logging in Sqlite3 databases.')
		parser.add_argument('--ofile', type=str, default = None, help='Output log filename. Defaults to log-yyyymmdd-hhmmss.sqlite3 where yyyymmdd-hhmmss is the start time when --log is asserted.')
		parser.add_argument('--sid', action='store_true', help = 'Display the sample ID while taking readings. The default is to not display the sample ID.')
		parser.add_argument('--interval', type=float, default = 1.0, help = 'Interval at which to take readings in seconds. Defaults to 1.0.')
		parser.add_argument('--debug', action='store_true', help = 'Debug.')
		args = parser.parse_args()
		
		# Build LabJack U3 object.
		u3i = u3Interface()
		
		if args.log == True:
			# If we have sqlite3 support...
			if canLog == True:
				# Build our logger.
				lggr = logger()
				lggr.setup(args.ofile)
		
		# Debugging
		if args.debug == True:
			u3i.setDebug(args.debug)
		
		# Set channel.
		if args.channel != None:
			u3i.setChannel(args.channel)
		
		# Set gain.
		if args.gain != None:
			u3i.setGain(args.gain)
		
		# Set units.
		if args.unit != None:
			u3i.setTUnit(args.unit)
		
		# Set thermocouple type.
		if args.tctype != None:
			u3i.setTCType(args.tctype)
		
		# Set vOffset.
		if args.voffset != None:
			u3i.setVOffset(args.voffset)
		
	except SystemExit:
		quit()
	except:
		tb = traceback.format_exc()
		print("Unhandled exception parsing CLI arguments:\n%s" %tb)
	
	try:
		#  Set up the U3.
		u3i.setup()
		
		# Blank sample ID string.
		sidStr = ""
		
		# Loop until code death.
		while(True):
			# Get reading timestamp.
			now = datetime.datetime.utcnow()
			
			# Get thermocouple voltage reading.
			tcv = u3i.getTcVolts()
			
			# Get cold junction temperature.
			ljt = u3i.getLJTemp()
			
			# Get the temperature.
			temp = u3i.getTCReading(tcv, ljt, unitComp = True)
			
			# Get the sample ID.
			sid = u3i.getSID()
			
			# If we want to display voltage...
			if (args.debug == True) or (args.cold == True):
				print("Cold junction temperature: %s %s" %(round(ljt, 1), u3i.getTUnit()))
			
			# If we want to display voltage...
			if (args.debug == True) or (args.volts == True):
				print("Thermocouple volts: %s V" %tcv)
			
			# Do we want to dump sample IDs?
			if args.sid == True:
				sidStr = "%s: " %u3i.getSID()
			
			# Dump the temp.
			print("%sThermocouple temp: %s %s" %(sidStr, round(temp, 1), u3i.getTUnit()))
			
			if (args.log == True) and (canLog == True):
				logStr = u3i.buildJsonString(now, u3i.getCJTemp(ljt, unitComp = True), tcv, temp, u3i.getTUnit())
				lggr.log(sid, logStr)
			
			# Wait specified amount of time before repeating.
			time.sleep(args.interval)
	
	except KeyboardInterrupt:
		print("\nCaught keyboard interupt.\n")
	except:
		tb = traceback.format_exc()
		print("Unhandled exception:\n%s" %tb)
	finally:
		# if we're logging make sure we clean up.
		if (canLog == True) and (args.log == True):
			# Try to clean up the logger.
			lggr.close()
		
		# Clean up.
		u3i.cleanup()