# Device (stubs) for BESSY II implemented in ophyd-async

Contains currently

* topup engine. Please use 
  ```python
    topup = TopUpSystem("TOPUPCC:", name="topup", target_current=25, acceptable_loss=0.1)
  ```
  see also `examples/topup.py` 

* 