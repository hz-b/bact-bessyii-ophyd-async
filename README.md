# Device (stubs) for BESSY II implemented in ophyd-async

Contains currently

* topup engine. Please use 
  ```python
  from bact_bessyii_ophyd_async.devices.topup_engine.system import TopUpSystem
  topup = TopUpSystem("TOPUPCC:", name="topup", target_current=25, acceptable_loss=0.1)
  ```
  see also `examples/topup.py` 

* kicker power converter: in particular interface for
  the diagnostic kickers

  For the horizontal one:
  ```python
  from bact_bessyii_ophyd_async.devices.pp.kicker_ps import KickerPS
  
  hk = KickerPS(prefix="PKDHKR:", name="hk")
  ```
  For the vertical one:
  ```python
  from bact_bessyii_ophyd_async.devices.pp.kicker_ps import KickerPS

  vk = KickerPS(prefix="PKDVKR:", name="vk")
  ```

  see also `examples/kicker_ps.py` 
  
* a delay

**NB** Please note the names are an essential parameter.
You can instaniate the device without it, but reading
will not (necessarily) return the data of all signals 
as expected.