var mongoose = require('mongoose');

var TemperatureEventSchema = new mongoose.Schema({
	date: Date,
	temperature: Number,
	humidity: Number,
	error: Boolean,
	exception: String,
	_id: mongoose.Schema.ObjectId

})

module.exports = mongoose.model('temperatureevents', TemperatureEventSchema);
