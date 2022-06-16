#!/bin/env python3
import sys
import os
import json

sys.path.append(os.path.join(sys.path[0],'..'))
from omsapi import OMSAPI



try:
    srv_1 = sys.argv[1]
    srv_2 = sys.argv[2]
    path = sys.argv[3].strip("/").split('/')
    workspace, folder, page = path[0], path[1], path[2]
except Exception as ex:
    print(ex)
    print("Usage: command server1.cern.ch server2.cern.ch path/to/page")
    sys.exit(1)

force_destination_check = True

#note: use cert_verify = False in case certificate chain is not installed
#omsapi_1 = OMSAPI("https://vocms0184.cern.ch/api", "v1", cert_verify=True)
omsapi_1 = OMSAPI("https://" + srv_1 + "/api", "v1", cert_verify=True)
omsapi_1.auth_krb()
q_1 = omsapi_1.query_metadata()

omsapi_2 = OMSAPI("https://" + srv_2 + "/api", "v1", cert_verify=True)
omsapi_2.auth_krb()
q_2 = omsapi_2.query_metadata()


workspace_id_to_path={1:{}, 2:{}}
workspace_path_to_id={1:{}, 2:{}}

def get_page( q, workspace, folder, page, srv):
    #extrac
    ret = {}
    #print(f"...getting workspaces query ({srv})...")
    workspaces = q.data("workspaces").json()["data"]
    workspace_id = None
    for ws in workspaces:
        if ws["attributes"]["path"] == workspace:
            workspace_id = ws["id"] 
            ret["workspace_title"] = ws["attributes"]["title"]
            ret["workspace_description"] = ws["attributes"]["description"]
        workspace_id_to_path[srv][ws["id"]] = ws["attributes"]["path"]
        workspace_path_to_id[srv][ws["attributes"]["path"]] = ws["id"]
    if not workspace_id:
        print("workspace not found in server " + str(srv))
        sys.exit(2)

    #print("...getting workspace/'id' query...")
 
    ws_folders = q.data("workspaces/" + str(workspace_id)).json()["data"]["attributes"]["folders"]
    folder_id = None
    page_id = None
    for fl in ws_folders:
        #print("checking",fl["attributes"]["path"])
        if fl["attributes"]["path"] == folder:
            folder_id = ws["id"] 
            ret["folder_title"] = fl["attributes"]["title"]
            ret["folder_description"] = fl["attributes"]["description"]
            for p in fl["attributes"]["pages"]:
                if p["attributes"]["path"] == page:
                    page_id = ret["page_id"] = p["id"]
                    ret["page_title"] = p["attributes"]["title"]
                    ret["page_description"] = p["attributes"]["title"]
                    break
            break
    if not folder_id:
        print("folder not found on the server " + str(srv))
        sys.exit(2)
    if not page_id:
        print("page not found on the server " + str(srv))
        ret["page_id"]=None
        #sys.exit(2)
    return ret


def parse_portlets(pprops, srv):
    components = {}
    for pp_ in pprops:
        pp = pp_["attributes"]
        #print(pp)
        portlet_attrs = pp["portlet"]["attributes"]
        pc_attrs = portlet_attrs["portlet_component"]["attributes"]
        pc_key = pc_attrs["type"] + '%' + pc_attrs["name"]
        #store component maybe
        if pc_key not in components:
          components[pc_key]= {"type": pc_attrs["type"], "name": pc_attrs["name"],"portlets":{},
                               "workspace":  workspace_id_to_path[srv][pc_attrs["workspace_id"]],
                               "workspace_id": pc_attrs["workspace_id"],
                               "config_schema": json.dumps(pc_attrs["config_schema"])
          }
        #store portlet maybe
        if portlet_attrs["title"] not in components[pc_key]["portlets"]:
          components[pc_key]["portlets"][portlet_attrs["title"]] = {
            "title": portlet_attrs["title"],
            "description": portlet_attrs["description"],
            "min_size_x": portlet_attrs["min_size_x"],
            "min_size_y": portlet_attrs["min_size_y"],
            "workspace": workspace_id_to_path[srv][portlet_attrs["workspace_id"]],
            "workspace_id": portlet_attrs["workspace_id"],
            "selectors_in": {},
            "selectors_out": {},
            "portlet_properties": {},
            "configuration": json.dumps(portlet_attrs["configuration"])
          }
        #store portlet properties
        ppobj = components[pc_key]["portlets"][portlet_attrs["title"]]["portlet_properties"]
        ppobj[pp["order_no"]] = {
            "order_no": pp["order_no"],
            "pos_x": pp["pos_x"],
            "pos_y": pp["pos_y"],
            "size_x": pp["size_x"],
            "size_y": pp["size_y"]
        }
        selobj_in = components[pc_key]["portlets"][portlet_attrs["title"]]["selectors_in"]
        for sel_ in portlet_attrs["selectors"]["in"]:
            sel = sel_["attributes"]
            if sel["name"] in selobj_in:
                continue
            selobj_in[sel["name"]] = {"name": sel["name"], "attribute": sel["attribute"],
                                      "operator": sel["operator"], "title": sel["title"],
                                      "description": sel["description"],
                                      "workspace": workspace_id_to_path[srv][sel["workspace_id"]],
                                      "workspace_id": sel["workspace_id"]
            }
          
        selobj_out = components[pc_key]["portlets"][portlet_attrs["title"]]["selectors_out"]
        for sel_ in portlet_attrs["selectors"]["out"]:
            sel = sel_["attributes"]
            if sel["name"] in selobj_out:
                continue
            selobj_out[sel["name"]] = {"name": sel["name"], "attribute": sel["attribute"],
                                       "operator": sel["operator"], "title": sel["title"],
                                       "description": sel["description"],
                                       "workspace": workspace_id_to_path[srv][sel["workspace_id"]],
                                       "workspace_id": sel["workspace_id"]
            }
    return components


def parse_controller(ctrl, srv):
  #print("CONTROLLER",json.dumps(ctrl))
  cc_in = ctrl["controller_component"]["attributes"]
  try:
      workspace_id_to_path[srv][cc_in["workspace_id"]]
  except:
      print(f"Error: unknown controller component {cc_in['name']} workspace id {cc_in['workspace_id']} in server {srv}")
  try:
      workspace_id_to_path[srv][ctrl["workspace_id"]]
  except:
      print(f"Error: unknown controller component {ctrl['title']} workspace id {ctrl['workspace_id']} in server {srv}")
  cc = {
    "name": cc_in["name"],
    "config_schema": json.dumps(cc_in["config_schema"]),
    "workspace": workspace_id_to_path[srv][cc_in["workspace_id"]],
    "workspace_id": cc_in["workspace_id"],
    "controller": {
        "title": ctrl["title"],
        "description": ctrl["description"],
        "configuration": ctrl["configuration"],
        "workspace": workspace_id_to_path[srv][ctrl["workspace_id"]],
        "workspace_id": ctrl["workspace_id"],
        "selectors": {}
    }
  }

  for sel_ in ctrl["selectors"]:
      sel = sel_["attributes"]
      if sel["name"] in cc["controller"]["selectors"]:
          continue
      cc["controller"]["selectors"][sel["name"]] = {"name": sel["name"], "attribute": sel["attribute"],
                                                    "operator": sel["operator"], "title": sel["title"],
                                                    "description": sel["description"],
                                                    "workspace": workspace_id_to_path[srv][sel["workspace_id"]],
                                                    "workspace_id": sel["workspace_id"]
      }


  return cc



def get_delta_keys(a,b, obj_name, optional=""):

    if a.keys() != b.keys():
      in_a = a.keys() - b.keys()
      if len(in_a):
        print(f"Error: {obj_name}s only in source: {in_a}" + ((" for " + optional) if optional else ""))
    
      in_b = b.keys() - a.keys()
      if len(in_b):
        print(f"Error: {obj_name}s only in destination: {in_b}" + (( " for " + optional) if optional else ""))

      final_list = list(set(list(a.keys()) + list(b.keys())) - set(a.keys()-b.keys()) - set(b.keys()-a.keys()))
    else:
      final_list = list(a.keys())
    return final_list


#query and make map of components represented in the input map
def find_components(pmap_in, q2):
    components = {}
    ws_portlets_cache = {}
    components_2 = q2.data("portlet_components").json()["data"]
    for ckey in pmap_in:
      match = False
      match_id = None
      match_workspace_id = None
      comp = pmap_in[ckey]
      for comp2_ in components_2:
          comp2 = comp2_["attributes"]
          #first try in same workspace:
          if comp2["workspace_id"] not in workspace_id_to_path[2]:
              print(f"Error: General DB inconsistency: component {comp2['name']} assigned to a non-existing workspace {comp2['workspace_id']} in destination")
              continue
          ws2 = workspace_id_to_path[2][comp2["workspace_id"]]
          if comp["workspace"] == ws2:
              #require name AND type for a match
              if comp2["type"] == comp["type"] and comp2["name"] == comp["name"]:
                  match = True
                  components[ckey]= {"type": comp2["type"], "name": comp2["name"],"portlets":{},
                                     "workspace":  ws2,
                                     "workspace_id": comp2["workspace_id"],
                                     "config_schema": json.dumps(comp2["config_schema"])
                  }
                  match_id = comp2["id"]
                  match_ws_id = comp2["workspace_id"]

      if not match:
          for comp2_ in components_2:
              comp2 = comp2_["attributes"]
              #first try in same workspace:
              #require name AND type for a match
              if comp2["type"] == comp["type"] and comp2["name"] == comp["name"]:
                  ws_2 = workspace_id_to_path[2][comp2["workspace_id"]]
                  match = True
                  print(f"Warning: component name {comp['name']} type {comp['type']} found in a different workspace from source ({comp['workspace']} != {ws_2})")
                  components[ckey]= {"type": comp2["type"], "name": comp2["name"],"portlets":{},
                                     "workspace":  ws2,
                                     "workspace_id": comp2["workspace_id"],
                                     "config_schema": json.dumps(comp2["config_schema"])
                  }
                  match_id = comp2["id"]
                  match_ws_id = comp2["workspace_id"]
      if not match:
          print(f"Error: Portlet component {comp} not found in destination")
      else:
          #find portlets
          for pkey in comp["portlets"]:
              portlet1=comp["portlets"][pkey]
              ws_pkey = portlet1["workspace"]
              portlet_match = False
              if ws_pkey in workspace_path_to_id[2].keys():
                  ordered_ws_list = [ws_pkey] + list(workspace_path_to_id[2].keys() - ws_pkey)
              else:
                  ordered_ws_list = list(workspace_path_to_id[2].keys())

              for ws2_pkey in ordered_ws_list:

                  ws2_id = workspace_path_to_id[2][ws2_pkey]
                  if not ws2_pkey in ws_portlets_cache:
                      #fetch portlets query
                      ws_portlets_cache[ws2_pkey] = q2.data("workspaces/" + str(ws2_id) + "/portlets").json()["data"]

                  for p2_ in ws_portlets_cache[ws2_pkey]:
                    p2 = p2_["attributes"]
                    if p2["title"] == portlet1["title"]:
                      
                      p2_comp = p2["portlet_component"]["attributes"]
                      if ws2_pkey == ws_pkey and p2_comp["workspace_id"] != ws2_id:
                          ws2_p = workspace_id_to_path[2][ws2_id]
                          print(f"Warning: Portlet component of portlet {p2['title']} not in the same workspace ({ws_pkey} != {ws2_p})")

                      pkey_mismatch = False
                      if p2_comp["name"] != comp["name"]:
                          if ws2_pkey == ws_pkey:
                              print(f"Warning: Destination component of Portlet {p2['title']} has a different name ({ comp['name']} != {p2_comp['name']})")
                          pkey_mismatch = True
                      if p2_comp["type"] != comp["type"] :
                          if ws2_pkey == ws_pkey:
                              print(f"Warning: Destination component of Portlet {p2['title']} has a different type ({ comp['type']} != {p2_comp['type']})")
                          pkey_mismatch = True
                      if not pkey_mismatch:
                          portlet_match = True
                          components[ckey]["portlets"][pkey] = {
                              "title": p2["title"],
                              "description": p2["description"],
                              "min_size_x": p2["min_size_x"],
                              "min_size_y": p2["min_size_y"],
                              "workspace": workspace_id_to_path[2][p2["workspace_id"]],
                              "workspace_id": p2["workspace_id"],
                              "selectors_in": {},
                              "selectors_out": {},
                              "portlet_properties": {},
                              "configuration": json.dumps(p2["configuration"])
                          }
                          #fill-in selectors 

                          selobj_in = components[ckey]["portlets"][pkey]["selectors_in"]
                          for sel_ in p2["selectors"]["in"]:
                              sel = sel_["attributes"]
                              if sel["name"] in selobj_in:
                                  continue
                              selobj_in[sel["name"]] = {"name": sel["name"], "attribute": sel["attribute"],
                                                        "operator": sel["operator"], "title": sel["title"],
                                                        "description": sel["description"],
                                                        "workspace": workspace_id_to_path[2][sel["workspace_id"]],
                                                        "workspace_id": sel["workspace_id"]
                              }

                          selobj_out = components[ckey]["portlets"][pkey]["selectors_out"]
                          for sel_ in p2["selectors"]["out"]:
                              sel = sel_["attributes"]
                              if sel["name"] in selobj_out:
                                  continue
                              selobj_out[sel["name"]] = {"name": sel["name"], "attribute": sel["attribute"],
                                                         "operator": sel["operator"], "title": sel["title"],
                                                         "description": sel["description"],
                                                         "workspace": workspace_id_to_path[2][sel["workspace_id"]],
                                                         "workspace_id": sel["workspace_id"]
                              }
                          #portlet found
                          break
                  if portlet_match:
                      #portlet found
                      break

    
    return components

#query and make map of portlet represented in the input map
def find_controller(c_in, q2):

    component = None
    ws_controllers_cache = {}
    match = False
    match_id = None
    match_workspace_id = None
    comp = c_in
    components_2 = q2.data("controller_components").json()["data"]
    for comp2_ in components_2:
          comp2 = comp2_["attributes"]
          #first try in same workspace:
          if comp2["workspace_id"] not in workspace_id_to_path[2]:
              print(f"Error: General DB inconsistency: controller component {comp2['name']} assigned to a non-existing workspace {comp2['workspace_id']} in destination")
              continue
          ws2 = workspace_id_to_path[2][comp2["workspace_id"]]
          if comp["workspace"] == ws2:
              #require name AND type for a match
              if comp2["name"] == comp["name"]:
                  match = True
                  component = {"name": comp2["name"], "controller": None,
                                     "workspace":  ws2,
                                     "workspace_id": comp2["workspace_id"],
                                     "config_schema": json.dumps(comp2["config_schema"])
                  }
                  match_id = comp2["id"]
                  match_ws_id = comp2["workspace_id"]

    if not match:
          for comp2_ in components_2:
              comp2 = comp2_["attributes"]
              #first try in same workspace:
              #require name AND type for a match
              if comp2["name"] == comp["name"]:
                  ws_2 = workspace_id_to_path[2][comp2["workspace_id"]]
                  match = True
                  print(f"Warning: ctrl component name {comp['name']} found in a different workspace from source ({comp['workspace']} != {ws_2})")
                  component = {"name": comp2["name"], "controller":None,
                                     "workspace":  ws2,
                                     "workspace_id": comp2["workspace_id"],
                                     "config_schema": json.dumps(comp2["config_schema"])
                  }
                  match_id = comp2["id"]
                  match_ws_id = comp2["workspace_id"]
    if not match:
       print(f"Error: Controller component {comp['name']} not found in destination")
       return None
    else:
        #find controller
        ctrl=comp["controller"]
        ws_pkey = ctrl["workspace"]
        ctrl_match = False
        if ws_pkey in workspace_path_to_id[2].keys():
            ordered_ws_list = [ws_pkey] + list(workspace_path_to_id[2].keys() - ws_pkey)
        else:
            ordered_ws_list = list(workspace_path_to_id[2].keys())

        controller_match = False
        for ws2_pkey in ordered_ws_list:

            ws2_id = workspace_path_to_id[2][ws2_pkey]
            if not ws2_pkey in ws_controllers_cache:
                  #fetch controllers query
                  ws_controllers_cache[ws2_pkey] = q2.data("workspaces/" + str(ws2_id) + "/controllers").json()["data"]

            for p2_ in ws_controllers_cache[ws2_pkey]:
                p2 = p2_["attributes"]
                if p2["title"] == ctrl["title"]:
                    #match ? check component 
                    p2_comp = p2["controller_component"]["attributes"]
                    if ws2_pkey == ws_pkey and p2_comp["workspace_id"] != ws2_id:
                        ws2_p = workspace_id_to_path[2][ws2_id]
                        print(f"Warning: Controller component of controller {p2['title']} not in the same workspace ({ws_pkey} != {ws2_p})")

                    if p2_comp["name"] != comp["name"]:
                        print(f"Error: Controller component of controller {p2['name']} is of different name ({ comp['name']} != {p2_comp['name']})")
                    else:
                        controller_match = True
                        component["controller"] = {
                            "title": p2["title"],
                            "description": p2["description"],
                            "workspace": workspace_id_to_path[2][p2["workspace_id"]],
                            "workspace_id": p2["workspace_id"],
                            "selectors": {},
                            "configuration": json.dumps(p2["configuration"])
                        }
                        #fill-in selectors 
                        selobj = component["controller"]["selectors"]
                        for sel_ in p2["selectors"]:
                            sel = sel_["attributes"]
                            if sel["name"] in selobj:
                                continue
                            selobj[sel["name"]] = {"name": sel["name"], "attribute": sel["attribute"],
                                                   "operator": sel["operator"], "title": sel["title"],
                                                   "description": sel["description"],
                                                   "workspace": workspace_id_to_path[2][sel["workspace_id"]],
                                                   "workspace_id": sel["workspace_id"]
                            }
                        #controller found
                        break
            if controller_match:
                break
                      
    return component




def comp_pc_name(cola, colb, name, key, silent=False):
      if silent:
          if cola[name] != colb[name]: print(f"Error: Portlet component '{key}' attribute {name} differs between source and dest.")
      else:
          if cola[name] != colb[name]: print(f"Error: Portlet component '{key}' attribute {name} differs between source: {cola[name]} and dest: {colb[name]}")

def comp_p_name(cola, colb, name, key, silent=False):
      if silent:
          if cola[name] != colb[name]: print(f"Error: Portlet '{key}' attribute {name} differs between source and dest.")
      else:
          if cola[name] != colb[name]: print(f"Error: Portlet '{key}' attribute {name} differs between source: {cola[name]} and dest: {colb[name]}")

def comp_sin_name(cola, colb, name, key):
      if cola[name] != colb[name]: print(f"Error: IN Selector '{key}' attribute {name} differs between source: {cola[name]} and dest: {colb[name]}")

def comp_sout_name(cola, colb, name, key):
      if cola[name] != colb[name]: print(f"Error: OUT Selector '{key}' attribute {name} differs between source: {cola[name]} and dest: {colb[name]}")

def comp_pp_name(cola, colb, name, key):
      if cola[name] != colb[name]: print(f"Error: Portlet '{key}' attribute {name} differs between source: {cola[name]} and dest: {colb[name]}")

def comp_cc_name(cola, colb, name, key, silent=False):
      if silent:
          if cola[name] != colb[name]: print(f"Error: Controller component {key} attribute {name} differs between source and dest.")
      else:
          if cola[name] != colb[name]: print(f"Error: Controller component {key} attribute {name} differs between source: {cola[name]} and dest: {colb[name]}")

def comp_ctrl_name(cola, colb, name, key, silent=False):
      if silent:
          if cola[name] != colb[name]: print(f"Error: Controller attribute {key} {name} differs between source and dest.")
      else:
          if cola[name] != colb[name]: print(f"Error: Controller attribute {key} {name} differs between source: {cola[name]} and dest: {colb[name]}")

def comp_csel_name(cola, colb, name, key):
      if cola[name] != colb[name]: print(f"Error: Controller Selector '{key}' variable {name} differs between source: {cola[name]} and dest: {colb[name]}")


def compare_portlets(a, b, compare_props=True):

    final_list = get_delta_keys(a, b, "portlet component")

    for pc in final_list:
      ac = a[pc]
      bc = b[pc]

      #shouldn't happen
      comp_pc_name(ac, bc, "type", pc)
      comp_pc_name(ac, bc, "name", pc)

      comp_pc_name(ac, bc, "workspace", pc)
      comp_pc_name(ac, bc, "config_schema", pc, silent=True)


      final_list_p = get_delta_keys(ac["portlets"], bc["portlets"], "portlet", "portlet component:" + pc)

      for p  in final_list_p:
        ap = ac["portlets"][p]
        bp = bc["portlets"][p]

        comp_p_name(ap, bp, "title", p)
        comp_p_name(ap, bp, "description", p)
        comp_p_name(ap, bp, "configuration", p, silent=True)
        comp_p_name(ap, bp, "min_size_x", p)
        comp_p_name(ap, bp, "min_size_y", p)
        comp_p_name(ap, bp, "workspace", p)

        final_list_sin = get_delta_keys(ap["selectors_in"], bp["selectors_in"], "IN selector", "portlet: " + p)
        final_list_sout = get_delta_keys(ap["selectors_out"], bp["selectors_out"], "OUT selector", "portlet: " + p)

        for s in final_list_sin:
          asel = ap["selectors_in"][s]
          bsel = ap["selectors_in"][s]
          comp_sin_name(asel, bsel, "name", s)
          comp_sin_name(asel, bsel, "title", s)
          comp_sin_name(asel, bsel, "description", s)
          comp_sin_name(asel, bsel, "attribute", s)
          comp_sin_name(asel, bsel, "operator", s)
          comp_sin_name(asel, bsel, "workspace", s)


        for s in final_list_sout:
          asel = ap["selectors_out"][s]
          bsel = ap["selectors_out"][s]
          comp_sout_name(asel, bsel, "name", s)
          comp_sout_name(asel, bsel, "title", s)
          comp_sout_name(asel, bsel, "description", s)
          comp_sout_name(asel, bsel, "attribute", s)
          comp_sout_name(asel, bsel, "operator", s)
          comp_sout_name(asel, bsel, "workspace", s)

        if compare_props:
          
          final_list_pp = get_delta_keys(ap["portlet_properties"], bp["portlet_properties"], "portlet propertie", "portlet: " + p + " (NOTE: p.property key is order number!)")
          for pp in final_list_pp:
            app = ap["portlet_properties"][pp]
            bpp = ap["portlet_properties"][pp]
          
            comp_pp_name(app, bpp, "order_no", pp)
            comp_pp_name(app, bpp, "pos_x", pp)
            comp_pp_name(app, bpp, "pos_y", pp)
            comp_pp_name(app, bpp, "size_x", pp)
            comp_pp_name(app, bpp, "size_y", pp)

def compare_controllers(a, b):
        comp_cc_name(a, b, "name", a["name"])
        comp_cc_name(a, b, "config_schema", a["name"], silent=True)
        comp_cc_name(a, b, "workspace", a["name"])
        ac = a["controller"]
        bc = b["controller"]
        if bc == None:
            print(f"Error: controller {a['name']} not found in destination")
            return
        comp_ctrl_name(ac, bc, "title", a["name"])
        comp_ctrl_name(ac, bc, "description", a["name"])
        comp_ctrl_name(ac, bc, "configuration", a["name"], silent=True)
        comp_ctrl_name(ac, bc, "workspace", a["name"])
        final_list_sel = get_delta_keys(ac["selectors"], bc["selectors"], "selector", "controller: " + ac["title"])
        for s in final_list_sel:
            asel = ac["selectors"][s]
            bsel = bc["selectors"][s]
            comp_csel_name(asel, bsel, "name", s)
            comp_csel_name(asel, bsel, "title", s)
            comp_csel_name(asel, bsel, "description", s)
            comp_csel_name(asel, bsel, "attribute", s)
            comp_csel_name(asel, bsel, "operator", s)
            comp_csel_name(asel, bsel, "workspace", s)


def analysis(q_1, q_2, workspace, folder, page):

    #print("...getting pages...")

    page_1_info = get_page(q_1, workspace, folder, page, 1)
    page_2_info = get_page(q_2, workspace, folder, page, 2)

    if page_1_info["page_id"] == None:
        print("missing source page")
        sys.exit(2)

    #print("...getting page queries...")

    response_1_page = q_1.data("pages/"+str(page_1_info["page_id"])).json()

    if page_1_info["page_id"] != None:
        response_2_page = q_2.data("pages/"+str(page_2_info["page_id"])).json()

    page1_ctrl = response_1_page["data"]["attributes"]["controller"]
    
    page1_portlet_components = parse_portlets(response_1_page["data"]["attributes"]["portlets"], 1)

    page1_controller = None
    if (response_1_page["data"]["attributes"]["controller"]):
        page1_controller = parse_controller(response_1_page["data"]["attributes"]["controller"]["attributes"], 1)
    #print("summary tree source:")
    #print(json.dumps(page1_portlet_components, indent=2))

    #if page_1_info["page_id"] != None and False:
    if page_2_info["page_id"] != None:
        print("...page found in destination...")
        page2_portlet_components = parse_portlets(response_2_page["data"]["attributes"]["portlets"], 2)
        page2_controller = None
        if (response_2_page["data"]["attributes"]["controller"]):
            page2_controller = parse_controller(response_2_page["data"]["attributes"]["controller"]["attributes"], 2)

        #compare...
        print("...COMPARING PORTLETS...")
        compare_portlets(page1_portlet_components, page2_portlet_components, compare_props=True)
        print("...COMPARISON DONE...")
        if (page1_controller is None or page2_controller is None):
            if page1_controller is not None and page2_controller is None:
                print("Error: destination controller is null, while source is not null")
            if page2_controller is not None and page1_controller is None:
                print("Error: source controller is null, while destination is not null")
        else:
            print("...COMPARING CONTROLLERS...")
            compare_controllers(page1_controller, page2_controller)
            print("...COMPARISON DONE...")
        #sys.exit(0)
    if page_2_info["page_id"] == None or force_destination_check:
        if page_2_info["page_id"] == None:
            print("Warning: page not found in destination. Not inserted yet? Will run per-component analysis per source page...")
        else:
            print("...Running second set of checks on destination (force). Try swapping source and dest to check source...")
        page2_portlet_components = find_components(page1_portlet_components, q_2)
        print("...COMPARING PORTLETS (method 2)...")
        compare_portlets(page1_portlet_components, page2_portlet_components, compare_props=False)
        print("...COMPARISON DONE...")
        if page1_controller is not None:
            page2_controller = find_controller(page1_controller, q_2)
            print("...COMPARING CONTROLLERS (method 2)...")
            if page2_controller is None:
                print("Error: Controller not found in destination")
            else:
                compare_controllers(page1_controller, page2_controller)
            print("...COMPARISON DONE...")



analysis(q_1, q_2, workspace, folder, page)
