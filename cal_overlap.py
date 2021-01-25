import cv2
import os
import numpy as np

def cal_rotbbox_overlap(cnt1, cnt2):
    '''
    calculating overlap
    rotated bounding boxes are taken as contours(cnt)
    '''
    cnt1 = [int(x) for x in cnt1]
    cnt2 = [int(x) for x in cnt2]
    bl = max(max(cnt1), max(cnt2)) + 1 # border length
    cnt1 = np.array(cnt1).reshape((-1, 2))
    cnt2 = np.array(cnt2).reshape((-1, 2))
    
    canvas1 = np.zeros((bl, bl), np.uint8)
    canvas2 = canvas1.copy()
    cv2.fillPoly(canvas1, pts=[cnt1], color=50)
    cv2.fillPoly(canvas2, pts=[cnt2], color=50)
    area1, area2 = np.sum(canvas1 == 50), np.sum(canvas2 == 50)
    area_union = np.sum((canvas1 + canvas2) == 100)
    return area_union*1.0/(area1 + area2 - area_union)

def gt_dict(dpath):
    '''
    generate groundtruth dictionary
    given dataset depth
    '''
    seqs = []
    with open(os.path.join(dpath, 'list.txt')) as f:
        for l in f:
            seqs.append(l[:-1])

    d = {}
    for seq in seqs:
        d[seq] = []
        with open(os.path.join(dpath, seq, 'groundtruth.txt')) as f:
            for l in f:
                nums = l.split(',')
                coordinates = [float(x) for x in nums]
                d[seq].append(coordinates)

    return d

def visualize_bbox(dic):
    '''
    validation function
    '''
    for seq in dic:
        bboxes = dic['leaves']
        demo = cv2.imread(os.path.join('vot2016', 'leaves', '00000001.jpg'))
        s = demo.shape
        canvas = np.zeros(s, np.uint8)
        b = bboxes[0]
        print b
        cv2.circle(canvas, (int(b[0]), int(b[1])), 3, (255, 0, 0))
        cv2.circle(canvas, (int(b[2]), int(b[3])), 3, (0, 255, 0))
        cv2.circle(canvas, (int(b[4]), int(b[5])), 3, (0, 0, 255))
        cv2.circle(canvas, (int(b[6]), int(b[7])), 3, (255, 255, 255))
        cv2.imshow(seq, canvas)
        cv2.imwrite('1.jpg', canvas)
        cv2.waitKey(10000)

vot16_path = 'vot2016'
vot15_path = 'vot2015'

dic16 = gt_dict(vot16_path)
dic15 = gt_dict(vot15_path)

# visualize_bbox(dic16)

# cal vot overlap
overlap1516 = {}
for seq in dic15:
    overlap1516[seq] = []
    for i in range(len(dic15[seq])):
        tmp = cal_rotbbox_overlap(dic15[seq][i], dic16[seq][i])
        overlap1516[seq].append(tmp)

    print 'calculated overlap of ' + seq

# report overlap ratio
total_len = 0
total_overlap = 0
for seq in overlap1516:
    seq_len = len(overlap1516[seq])
    mean_overlap = np.mean(overlap1516[seq])
    total_len += seq_len
    total_overlap += seq_len*mean_overlap
    print 'seq ' + seq + ' len:' + str(seq_len) + ' avg overlap: ' + str(mean_overlap)

print 'all frame number: ' + str(total_len) + ' overlap: ' + str(total_overlap/total_len)
