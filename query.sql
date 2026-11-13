-- ============================================================
-- INSERT queries (column list only)
--  * Section header "-- [insert<TYPE>]" : insertP6, insertP7, insertD1, insertD2
--  * {table} is replaced with config.json "info.<type>.table"
--  * VALUES (...) is generated in python: one "?" per column, in this order
--  * Column order must match DataFrame order: plan_dt, plan_sq, then CSV columns after drop_column
-- ============================================================

-- [insertP6]
INSERT INTO {table} (
    plan_dt, plan_sq, doc_cd, ord_bc, plan_bc,
    dlv_cust, fileid, mng_bc, data_bc, code_serial,
    part_nm, work_bc, alc_cd, cust_fac, yest_out,
    prod_qty1, prod_qty2, prod_qty3, d01t, d02t,
    d03t, d04t, d05t, d06t, d07t,
    d08t, d09t, d010t, d0, d11t,
    d12t, d13t, d14t, d15t, d16t,
    d17t, d18t, d19t, d110t, d1,
    d21t, d22t, d23t, d24t, d25t,
    d26t, d27t, d28t, d29t, d210t,
    d2, d31t, d32t, d33t, d34t,
    d35t, d36t, d37t, d38t, d39t,
    d310t, d3, d41t, d42t, d43t,
    d44t, d45t, d46t, d47t, d48t,
    d49t, d410t, d4, rem_dqty, tot_qty,
    car_cd, work_bc2
)

-- [insertP7]
INSERT INTO {table} (
    plan_dt, plan_sq, doc_cd, ord_bc, plan_bc,
    dlv_cust, fileid, mng_bc, data_bc, code_serial,
    part_nm, work_bc, alc_cd, cust_fac, yest_out,
    prod_qty1, prod_qty2, prod_qty3, d0, d1,
    d2, d3, d4, d5, d6,
    d7, d8, d9, d10, d11,
    d12, rem_dqty, ord_sum, mitu, pre_seq,
    rem_qty, next_qty, tot_qty, car_cd, work_bc2
)

-- [insertD1]
INSERT INTO {table} (
    insp_dt, insp_sq, doc_cd, dlv_cust, cust_fac,
    part_cd, dlv_dt, dlv_no, dlv_part, in_source,
    in_bc, dlv_qty, in_qty, in_amt, in_code,
    in_up, in_dt, pur_doc, pur_part, lc_seq,
    lc_qty, lc_amt, lc_no, pack_up, pack_qty,
    shop_code, mat_doc, mat_part, mat_year, cury_bc,
    flt
)

-- [insertD2]
INSERT INTO {table} (
    plan_dt, plan_sq, doc_cd, dlv_cust, cust_fac,
    part_cd, cur_stock, real_stock, yest_out, d0_tm1,
    d0_tm2, d0_tm3, d0_tm4, d0_tm5, d0_tm6,
    d0_tm7, d0_tm8, d0_tm9, d0_tm10, d0,
    d1_tm1, d1_tm2, d1_tm3, d1_tm4, d1_tm5,
    d1_tm6, d1_tm7, d1_tm8, d1_tm9, d1_tm10,
    d1, d2_tm1, d2_tm2, d2_tm3, d2_tm4,
    d2_tm5, d2_tm6, d2_tm7, d2_tm8, d2_tm9,
    d2_tm10, d2, d3_tm1, d3_tm2, d3_tm3,
    d3_tm4, d3_tm5, d3_tm6, d3_tm7, d3_tm8,
    d3_tm9, d3_tm10, d3, d4_tm1, d4_tm2,
    d4_tm3, d4_tm4, d4_tm5, d4_tm6, d4_tm7,
    d4_tm8, d4_tm9, d4_tm10, d4, d5,
    d6, d7, d8, d9, d10,
    d11, d12, d13, d14, d15,
    d16, d17, d18, d19, d20,
    d21, d22, d23, d24, d25,
    d26, d27, d28, d29, d30,
    d31, rem_qty
)
